import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class TransformerEncoder(nn.Module):
    def __init__(
        self,
        vocab_size,
        embed_dim,
        num_heads,
        num_layers,
        hidden_dim,
        dropout=0.1,
        pad_idx=0,
        max_len=512,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.pos_encoding = nn.Parameter(torch.zeros(1, max_len, embed_dim))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(embed_dim)

    def forward(self, x, mask=None):
        # x: (B, T)
        B, T = x.size()
        embed = self.embedding(x) * self.scale
        embed = embed + self.pos_encoding[:, :T, :]
        embed = self.dropout(embed)

        # src_key_padding_mask: (B, T) - True for padded elements
        output = self.encoder(embed, src_key_padding_mask=mask)
        return output


class BiaffineAttention(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.1):
        super().__init__()
        self.head_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.dep_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

        # U * W * V
        self.U = nn.Parameter(torch.Tensor(hidden_dim, output_dim, hidden_dim))
        self.bias = nn.Parameter(torch.Tensor(output_dim))

        nn.init.xavier_uniform_(self.U)
        nn.init.zeros_(self.bias)

    def forward(self, heads, deps):
        # heads: (B, T, H)
        # deps: (B, T, H)

        head_out = self.head_mlp(heads)  # (B, T, H')
        dep_out = self.dep_mlp(deps)  # (B, T, H')

        # Bilinear: head @ U @ dep.T
        # (B, 1, T, H') @ (H', O, H') -> (B, O, T, H')
        # This is complex to broadcast. Standard biaffine implementation often splits:
        # Arc (output_dim=1) and Label (output_dim=num_labels).

        # Simplified calculation for generic use
        B, T, H = head_out.size()
        O = self.U.size(1)

        # (B, T, H) @ (H, O*H) -> (B, T, O*H) -> (B, T, O, H)
        U_flat = self.U.view(H, O * H)
        head_U = torch.matmul(head_out, U_flat).view(B, T, O, H)

        # (B, T, O, H) @ (B, T, H, 1) -> (B, T, O, 1) ? No, we want score between pairs.
        # We generally want (B, T_head, T_dep) for Arcs.
        pass


class DeepBiaffineAttention(nn.Module):
    """
    Standard Dozat & Manning (2017) Style Biaffine
    """

    def __init__(self, input_dim, hidden_dim, num_labels=1, dropout=0.1):
        super().__init__()
        # Arc MLPs
        self.arc_head_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(dropout)
        )
        self.arc_dep_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(dropout)
        )

        # Label MLPs
        self.rel_head_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(dropout)
        )
        self.rel_dep_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(dropout)
        )

        # Arc Biaffine: (H, 1, H) -> Scores (B, T, T)
        self.arc_U = nn.Parameter(torch.Tensor(hidden_dim, hidden_dim))

        # Rel Biaffine: (H, num_labels, H) -> Scores (B, T, T, num_labels)
        self.rel_U = nn.Parameter(torch.Tensor(hidden_dim, num_labels * hidden_dim))
        self.rel_bias = nn.Parameter(torch.Tensor(num_labels))  # Bias usually for rels

        self.num_labels = num_labels
        self.hidden_dim = hidden_dim

        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.arc_U)
        nn.init.xavier_uniform_(self.rel_U)
        nn.init.zeros_(self.rel_bias)

    def forward(self, x):
        # x: (B, T, input_dim)

        # Arc Scores
        arc_h = self.arc_head_mlp(x)  # (B, T, H)
        arc_d = self.arc_dep_mlp(x)  # (B, T, H)

        # (B, T, H) @ (H, H) -> (B, T, H)
        # (B, T, H) @ (B, H, T) -> (B, T, T)
        arc_scores = torch.matmul(
            torch.matmul(arc_h, self.arc_U), arc_d.transpose(1, 2)
        )

        # Rel Scores
        rel_h = self.rel_head_mlp(x)  # (B, T, H)
        rel_d = self.rel_dep_mlp(x)  # (B, T, H)

        # (B, T, H) -> (B, T, 1, H)
        # U: (H, L*H)
        # (B, T, 1, H) @ (H, L*H) -> (B, T, 1, L*H) -> (B, T, L, H)
        # @ (B, 1, T, H)^T is tricky for all pairs.
        # Usually we only need Rel scores for the *predicted* heads or gold heads.
        # But for full output we return computed tensors.

        return arc_scores, rel_h, rel_d, self.rel_U


class CombinedTransformerBiaffine(nn.Module):
    """
    Architecture:
    1. Transformer Encoder (Shared)
    2. Tagger Head (Linear)
    3. Parser Head (BiLSTM -> Biaffine)
    """

    def __init__(
        self,
        vocab_size,
        embed_dim,
        enc_heads,
        enc_layers,
        pos_vocab_size,
        num_rels,
        hidden_dim=256,
        lstm_layers=1,
        dropout=0.1,
    ):
        super().__init__()

        # 1. Shared Encoder
        self.encoder = TransformerEncoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            num_heads=enc_heads,
            num_layers=enc_layers,
            hidden_dim=hidden_dim * 2,
            dropout=dropout,
        )

        # 2. Tagger Head (Simple Linear)
        self.tagger = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, pos_vocab_size),
        )

        # 3. Parser Head Components
        # "Thin BiLSTM"
        self.parser_lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=lstm_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if lstm_layers > 1 else 0,
        )

        self.lstm_proj = nn.Linear(
            hidden_dim * 2, hidden_dim * 2
        )  # Project back if needed or keep size

        # Biaffine Attention (using Dozat & Manning style)
        self.biaffine = DeepBiaffineAttention(
            input_dim=hidden_dim * 2,  # BiLSTM output
            hidden_dim=hidden_dim,
            num_labels=num_rels,
            dropout=dropout,
        )

    def forward(self, x, mask=None):
        # x: (B, T)

        # 1. Encode
        enc_out = self.encoder(x, mask)  # (B, T, E)

        # 2. Tagging
        pos_logits = self.tagger(enc_out)  # (B, T, P)

        # 3. Parsing
        lstm_out, _ = self.parser_lstm(enc_out)  # (B, T, 2*H)
        # lstm_out = self.lstm_proj(lstm_out)

        arc_scores, rel_h, rel_d, rel_U = self.biaffine(lstm_out)

        return {
            "pos_logits": pos_logits,
            "arc_scores": arc_scores,
            "rel_h": rel_h,
            "rel_d": rel_d,
            "rel_U": rel_U,
            "enc_out": enc_out,
        }

    def decode_rels(self, rel_h, rel_d, rel_U, heads):
        # Calculate relation scores only for specific heads (e.g. gold or predicted)
        # heads: (B, T) indices of heads
        B, T, H = rel_h.size()
        L = rel_U.shape[0] // H  # Actually U is (H, L*H). Wait, simpler logic:

        # rel_U: (H, L*H) -> reshape (H, L, H) ? No.
        # Let's verify dimensions from DeepBiaffine implementation
        # Usually: bilinear(x_i, y_j) = x_i @ U @ y_j + bias
        # Here we want efficient batch.

        # Gather rel_d for the selected heads? No, rel_d corresponds to dependent (i)
        # rel_h corresponds to head (j). We want score for (head[i], i).

        # Gather head representations:
        # heads: (B, T) -> need to gather vectors from rel_h
        # rel_h: (B, T, H)

        batch_indices = torch.arange(B, device=rel_h.device).unsqueeze(1).expand(B, T)
        selected_heads = rel_h[batch_indices, heads]  # (B, T, H)

        # (B, T, H) @ (H, L*H) -> (B, T, L*H) -> (B, T, L, H)
        L = self.biaffine.num_labels
        H = self.biaffine.hidden_dim

        U_reshaped = rel_U.view(H, L * H)

        # (B, T, H) @ (H, L*H)
        combined = torch.matmul(selected_heads, U_reshaped)  # (B, T, L*H)
        combined = combined.view(B, T, L, H)

        # (B, T, L, H) * (B, T, 1, H) (dependent) -> sum dim -1
        dep_expanded = rel_d.unsqueeze(2)  # (B, T, 1, H)

        scores = torch.sum(combined * dep_expanded, dim=-1)  # (B, T, L)
        scores = scores + self.biaffine.rel_bias

        return scores


class SyllableMorphModel(nn.Module):
    """
    Morphological Analyzer (Syllable -> POS Tags)
    Transformer Encoder -> Linear -> (CRF optional, using simple Linear + Greedy/Viterbi for now)
    """

    def __init__(
        self,
        vocab_size,  # Number of characters/syllables
        embed_dim,
        num_heads,
        num_layers,
        num_tags,  # BIO Tags count
        hidden_dim=256,
        dropout=0.1,
    ):
        super().__init__()
        self.encoder = TransformerEncoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            num_heads=num_heads,
            num_layers=num_layers,
            hidden_dim=hidden_dim,
            dropout=dropout,
        )
        self.fc = nn.Linear(embed_dim, num_tags)

    def forward(self, x, mask=None):
        out = self.encoder(x, mask)
        logits = self.fc(out)
        return logits
