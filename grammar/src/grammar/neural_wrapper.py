import torch
import os
from .model import CombinedTransformerBiaffine, SyllableMorphModel
from .dataset import Vocab
from .bio_helper import convert_morphemes_to_bio
import torch.nn as nn
import torch.optim as optim


class NeuralWrapper:
    def __init__(self, model_path=None, morph_model_path=None, device="cpu"):
        self.device = device
        self.model = None  # Syntax Model
        self.morph_model = None  # Morph Model

        self.char_vocab = None
        self.pos_vocab = None
        self.deprel_vocab = None

        self.morph_char_vocab = None
        self.morph_tag_vocab = None

        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, "data")

        if model_path is None:
            model_path = os.path.join(data_dir, "neural_model.pt")

        if morph_model_path is None:
            morph_model_path = os.path.join(data_dir, "neural_morph_model.pt")

        if os.path.exists(model_path):
            self.load(model_path)
        else:
            print(f"Warning: Syntax Neural model not found at {model_path}")

        if os.path.exists(morph_model_path):
            self.load_morph(morph_model_path)
        else:
            print(f"Warning: Morph Neural model not found at {morph_model_path}")

    def load(self, path):
        print(f"Loading syntax neural model from {path}...")
        try:
            checkpoint = torch.load(path, map_location=self.device, weights_only=False)
            self.char_vocab = checkpoint["char_vocab"]
            self.pos_vocab = checkpoint["pos_vocab"]
            self.deprel_vocab = checkpoint["deprel_vocab"]

            self.model = CombinedTransformerBiaffine(
                vocab_size=len(self.char_vocab),
                embed_dim=256,
                enc_heads=4,
                enc_layers=4,
                pos_vocab_size=len(self.pos_vocab),
                num_rels=len(self.deprel_vocab),
                hidden_dim=256,
                lstm_layers=1,
            )
            self.model.load_state_dict(checkpoint["model"])
            self.model.to(self.device)
            self.model.eval()
            print("Syntax Neural model loaded successfully.")
        except Exception as e:
            print(f"Failed to load syntax neural model: {e}")
            self.model = None

    def load_morph(self, path):
        print(f"Loading morph neural model from {path}...")
        try:
            checkpoint = torch.load(path, map_location=self.device, weights_only=False)
            self.morph_char_vocab = checkpoint["char_vocab"]
            self.morph_tag_vocab = checkpoint["tag_vocab"]

            num_tags = len(self.morph_tag_vocab)
            self.morph_model = SyllableMorphModel(
                vocab_size=len(self.morph_char_vocab),
                embed_dim=128,
                num_heads=4,
                num_layers=2,
                num_tags=num_tags,
                hidden_dim=256,
                dropout=0.1,
            )
            self.morph_model.load_state_dict(checkpoint["model"])
            self.morph_model.to(self.device)
            self.morph_model.eval()
            print("Morph Neural model loaded successfully.")
        except Exception as e:
            print(f"Failed to load morph neural model: {e}")
            self.morph_model = None

    def predict_morph(self, text):
        """
        Single Sentence Morphological Analysis (Wrapper for Batch)
        """
        results = self.predict_morph_batch([text])
        return results[0] if results else []

    def predict_morph_batch(self, texts: list) -> list:
        """
        Batch Morphological Analysis
        Args:
            texts: List[str] (list of raw sentences/eojeols)
        Returns:
            List[List[Tuple[surface, pos]]]
        """
        if not self.morph_model or not texts:
            return [[] for _ in texts]

        self.morph_model.eval()

        # 1. Prepare Batch
        batch_chars = [list(t) for t in texts]
        lengths = [len(c) for c in batch_chars]
        max_len = max(lengths)

        # Tensorize & Pad
        # Initialize with 0 (pad_idx)
        # Note: Vocabulary must handle 0 as PAD or UNK. usually 0 is PAD.
        # Check model.py: TransformerEncoder defaults pad_idx=0.

        batch_size = len(texts)
        x = torch.zeros((batch_size, max_len), dtype=torch.long, device=self.device)
        mask = torch.ones(
            (batch_size, max_len), dtype=torch.bool, device=self.device
        )  # True = Padded (Ignored)

        for i, chars in enumerate(batch_chars):
            # Map chars to IDs
            # UNK handling if needed (using .get with default?)
            # Assuming vocab has __getitem__ handling UNK or we need manual check
            # defaults to 1 (UNK) if not found?
            # Existing code used `self.morph_char_vocab[c]` which might throw if missing?
            # Let's assume strict vocab or vocab object handles it.
            # `Vocab` usually has unknown token handling.

            ids = [self.morph_char_vocab[c] for c in chars]
            length = len(ids)

            x[i, :length] = torch.tensor(ids, dtype=torch.long)
            mask[i, :length] = False  # False = Not Padded (Attend)

        with torch.no_grad():
            # (B, T, NumTags)
            logits = self.morph_model(x, mask=mask)
            tag_ids_batch = logits.argmax(dim=-1).tolist()

            results = []
            for i, tag_ids in enumerate(tag_ids_batch):
                # Decode only valid length
                valid_len = lengths[i]
                valid_tag_ids = tag_ids[:valid_len]
                valid_chars = batch_chars[i]

                tags = [self.morph_tag_vocab.get_item(t) for t in valid_tag_ids]

                # Decode BIO for this item
                morphemes = []
                current_surf = ""
                current_pos = None

                for char, tag in zip(valid_chars, tags):
                    if tag.startswith("B-"):
                        if current_surf:
                            morphemes.append((current_surf, current_pos))
                        current_surf = char
                        current_pos = tag[2:]
                    elif tag.startswith("I-"):
                        current_surf += char
                        if current_pos is None:
                            current_pos = tag[2:]
                    else:
                        if current_surf:
                            morphemes.append((current_surf, current_pos))
                            current_surf = ""
                            current_pos = None

                if current_surf:
                    morphemes.append((current_surf, current_pos))

                results.append(morphemes)

            return results

    def online_train_morph(self, text: str, correct_morphemes: list) -> float:
        """
        Online Learning for Morphological Analyzer

        Args:
            text: Raw sentence text (e.g. "오늘 날씨가 좋다")
            correct_morphemes: List of (surf, pos) (e.g. [("오늘", "NNG"), ...])

        Returns:
            loss value
        """
        if not self.morph_model:
            print("Warning: Morph model is not loaded. Cannot train.")
            return 0.0

        # Validate reconstruction
        recon = "".join(m[0] for m in correct_morphemes)
        if text.replace(" ", "") != recon:
            # Token mismatch (e.g. irregular conjugation/contraction)
            # Skip complex cases in online learning for safety
            # print(f"Skip online training: Mismatch '{text}' vs '{recon}'")
            return 0.0

        # Convert to BIO
        chars, tags = convert_morphemes_to_bio(correct_morphemes)

        # Prepare inputs
        self.morph_model.train()

        # Build tensors (Single Batch)
        # Note: We must handle new characters/tags dynamically?
        # For now, UNK for new chars. Tags must be in vocab or ignored.

        # Add unknown tags to vocab if needed?
        # Online learning usually implies expanding vocab.
        # But changing vocab size invalidates model weights (dense layer shape).
        # So we can only train on KNOWN tags.

        form_ids = [self.morph_char_vocab[c] for c in chars]
        tag_ids = []
        for t in tags:
            tid = self.morph_tag_vocab[t]
            if tid is None:  # Vocab returns UNK (which is usually index 1 or similar)
                # Check if UNK
                pass
            tag_ids.append(tid)

        x = torch.tensor([form_ids], dtype=torch.long).to(self.device)
        y = torch.tensor([tag_ids], dtype=torch.long).to(self.device)

        # Optimizer
        # Create fresh optimizer for this step? Or keep one?
        # For online learning, creating one every time is inefficient but stateless.
        # Ideally, we should keep it self.optimizer but requires state management.
        # Let's create a ephemeral one with small LR.
        optimizer = optim.Adam(
            self.morph_model.parameters(), lr=1e-4, weight_decay=1e-5
        )  # Low LR for stability
        criterion = nn.CrossEntropyLoss(ignore_index=0)

        optimizer.zero_grad()

        # Forward
        # Mask is all False (no padding)
        logits = self.morph_model(x)  # (1, T, NumTags)

        num_tags = len(self.morph_tag_vocab)
        loss = criterion(logits.view(-1, num_tags), y.view(-1))

        loss.backward()
        optimizer.step()

        return loss.item()

    def predict(self, forms):
        """
        Args:
            forms: List[str] (morphemes or words)
        Returns:
            List[Dict] with 'pos', 'head', 'deprel'
        """
        if not self.model:
            return None

        self.model.eval()
        with torch.no_grad():
            # Prepare Input
            # Prepend ROOT
            input_forms = ["<ROOT>"] + forms
            form_ids = [self.char_vocab[f] for f in input_forms]
            x = torch.tensor([form_ids], dtype=torch.long).to(self.device)

            # Forward
            output = self.model(x)

            # Decode POS
            pos_logits = output["pos_logits"]  # (1, T, P)
            pos_ids = pos_logits.argmax(dim=-1).squeeze(0).tolist()  # (T)

            # Decode Arc (Heads)
            # arc_scores: (1, T, T) -> (1, T_dep, T_head)
            # Greedy decoding: argmax over heads for each dep
            arc_scores = output["arc_scores"]  # (1, T, T)
            # arc_scores[0, i, j] = score of j being head of i?
            # In training: arc_scores corresponds to (head, dep) if using head @ U @ dep.T?
            # Wait, implementation: `torch.matmul(head_U, dep.T)`
            # shape: `arc_scores = torch.matmul(torch.matmul(arc_h, self.arc_U), arc_d.transpose(1, 2))`
            # arc_h (B, T, H) @ U (H, H) -> (B, T, H) [Heads]
            # @ arc_d.T (B, H, T) [Deps] -> (B, T, T) [Head x Dep]
            # So arc_scores[b, h, d] is score for (head=h, dep=d).
            # We want to find best head h for each dep d.
            # So we iterate d (dim 2) and argmax over h (dim 1).

            heads = arc_scores.squeeze(0).argmax(dim=0).tolist()  # (T)

            # Decode Rels
            # Need tensor of predicted heads
            head_tensor = torch.tensor([heads], dtype=torch.long).to(self.device)
            rel_scores = self.model.decode_rels(
                output["rel_h"], output["rel_d"], output["rel_U"], head_tensor
            )  # (1, T, L)
            rel_ids = rel_scores.argmax(dim=-1).squeeze(0).tolist()  # (T)

            # Construct Result (Skip ROOT)
            results = []
            for i in range(1, len(input_forms)):
                results.append(
                    {
                        "form": input_forms[i],
                        "pos": self.pos_vocab.get_item(pos_ids[i]),
                        "head": heads[i],  # This index includes ROOT (0). 0 means Root.
                        "deprel": self.deprel_vocab.get_item(rel_ids[i]),
                    }
                )

            return results
