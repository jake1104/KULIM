import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class CharCNNEmbedding(nn.Module):
    def __init__(self, vocab_size, embed_dim, char_embed_dim=32, kernel_sizes=[2, 3, 4]):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.char_embed = nn.Embedding(256, char_embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(char_embed_dim, embed_dim // 4, k, padding=k // 2)
            for k in kernel_sizes
        ])
        self.proj = nn.Linear(embed_dim + embed_dim, embed_dim)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x, char_ids=None):
        word_emb = self.embedding(x)
        if char_ids is not None:
            char_emb = self.char_embed(char_ids)
            char_emb = char_emb.permute(0, 2, 1)
            conv_outs = []
            for conv in self.convs:
                conv_out = conv(char_emb)
                conv_out = F.relu(conv_out)
                conv_out = F.adaptive_max_pool1d(conv_out, 1).squeeze(-1)
                conv_outs.append(conv_out)
            char_feat = torch.cat(conv_outs, dim=-1)
            combined = torch.cat([word_emb, char_feat], dim=-1)
            word_emb = self.proj(combined)
        return self.dropout(word_emb)


class LightweightTransformerEncoder(nn.Module):
    def __init__(self, embed_dim, num_heads, num_layers, hidden_dim, dropout=0.1, max_len=128):
        super().__init__()
        self.embed_dim = embed_dim
        self.pos_encoding = nn.Parameter(torch.zeros(1, max_len, embed_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=num_heads,
            dim_feedforward=hidden_dim, dropout=dropout,
            batch_first=True, activation='gelu',
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(embed_dim)
        self.scale = math.sqrt(embed_dim)

    def forward(self, x, mask=None):
        B, T = x.size()
        x = x * self.scale + self.pos_encoding[:, :T, :]
        x = self.encoder(x, src_key_padding_mask=mask)
        return self.norm(x)


class SyllableMorphModel(nn.Module):
    def __init__(self, vocab_size, num_tags):
        super().__init__()
        embed_dim = 128
        self.embedding = CharCNNEmbedding(vocab_size, embed_dim)
        self.encoder = LightweightTransformerEncoder(
            embed_dim=embed_dim,
            num_heads=4,
            num_layers=2,
            hidden_dim=256,
            dropout=0.1,
        )
        self.classifier = nn.Linear(embed_dim, num_tags)

    def forward(self, x, char_ids=None, mask=None):
        x = self.embedding(x, char_ids)
        x = self.encoder(x, mask)
        return self.classifier(x)


class SimpleTagger(nn.Module):
    def __init__(self, vocab_size, pos_vocab_size):
        super().__init__()
        embed_dim = 96
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.pos_enc = nn.Parameter(torch.zeros(1, 128, embed_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=4,
            dim_feedforward=192, dropout=0.1,
            batch_first=True, activation='gelu',
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=2)
        self.classifier = nn.Linear(embed_dim, pos_vocab_size)
        self.scale = math.sqrt(embed_dim)

    def forward(self, x, mask=None):
        B, T = x.size()
        x = self.embedding(x) * self.scale + self.pos_enc[:, :T, :]
        x = self.encoder(x, src_key_padding_mask=mask)
        return self.classifier(x)


if __name__ == "__main__":
    model = SimpleTagger(vocab_size=1000, pos_vocab_size=30)
    x = torch.randint(1, 100, (2, 10))
    out = model(x)
    print(f"SimpleTagger output: {out.shape}")
