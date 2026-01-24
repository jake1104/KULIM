import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import os
from .model import CombinedTransformerBiaffine, SyllableMorphModel
from .dataset import CoNLLUDataset, collate_fn, SyllableBIODataset, collate_fn_morph


class NeuralTrainer:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = None
        self.dataset = None

    def train(
        self,
        corpus_path,
        save_path="neural_model.pt",
        epochs=10,
        batch_size=32,
        lr=1e-3,
    ):
        print(f"Loading dataset from {corpus_path}...")
        self.dataset = CoNLLUDataset(corpus_path, build_vocab=True)

        train_loader = DataLoader(
            self.dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn
        )

        # Init Model
        print("Initializing CombinedTransformerBiaffine...")
        self.model = CombinedTransformerBiaffine(
            vocab_size=len(self.dataset.char_vocab),  # Word vocab actually
            embed_dim=256,
            enc_heads=4,
            enc_layers=4,
            pos_vocab_size=len(self.dataset.pos_vocab),
            num_rels=len(self.dataset.deprel_vocab),
            hidden_dim=256,
            lstm_layers=1,  # "Thin"
        ).to(self.device)

        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        # Loss Functions
        pos_criterion = nn.CrossEntropyLoss(ignore_index=0)  # Pad
        arc_criterion = nn.CrossEntropyLoss(
            ignore_index=-1
        )  # Heads can be 0 (Root), Pad should be ignored? Head 0 is valid.
        # Masking required for Arc/Rel loss ideally
        rel_criterion = nn.CrossEntropyLoss(ignore_index=0)

        print(f"Start Training on {self.device} for {epochs} epochs...")

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0

            for batch in train_loader:
                forms = batch["forms"].to(self.device)
                pos_targets = batch["pos"].to(self.device)
                head_targets = batch["heads"].to(self.device)
                rel_targets = batch["deprels"].to(self.device)
                mask = batch["mask"].to(self.device)  # True is padding

                optimizer.zero_grad()

                output = self.model(forms, mask=mask)

                # 1. POS Loss
                # Output: (B, T, P) -> (B*T, P)
                # Target: (B, T) -> (B*T)
                pos_loss = pos_criterion(
                    output["pos_logits"].view(-1, output["pos_logits"].shape[-1]),
                    pos_targets.view(-1),
                )

                # 2. Arc Loss
                # Output: arc_scores (B, T, T) -> Score for each possible head
                # Target: head_idx (B, T)
                # B, T, T = output['arc_scores'].shape
                # Flatten: (B*T, T)
                # Target: (B*T) containing indices [0, T-1]

                # Note: arc_scores are for (dependent, head).
                # Biaffine output logic: arc_scores[b, i, j] = score of i being head of j? Or j head of i?
                # My implementation: head @ U @ dep.T
                # arc_scores[b, i, j] corresponds to head=i, dep=j (cols are deps)
                # We want to predict head for each dep j.
                # So for dep j, scores over all i are at arc_scores[b, :, j].
                # PyTorch CrossEntropy expects (N, C) where C is classes.
                # Here C is the sentence length T.
                # Input to Loss: (B, T_head, T_dep). We classify 'head' for each 'dep'.
                # So we transpose to (B, T_dep, T_head) -> Flatten (B*T_dep, T_head)

                # Wait, shape of arc_scores in implementation:
                # arc_scores = (B, T, T) from matmul(head, U, dep.T)
                # Head dim is dim 1, Dep dim is dim 2.
                # So arc_scores[b, h, d] is score for (head=h, dep=d).
                # For a given dep d, we want scores over all h: arc_scores[b, :, d].
                # We need (B, T_dep, T_head). So transpose(1, 2).

                arc_scores = output["arc_scores"].transpose(1, 2)  # (B, T_dep, T_head)
                B, T, _ = arc_scores.shape

                arc_loss = pos_criterion(  # reusing ignore_index=0? No, Pad mask handles it?
                    # We need to mask out padded tokens from Loss calculation.
                    # CrossEntropyLoss has ignore_index, but our class size T changes per batch?
                    # No, padded parts are just ignored if target is ignored.
                    # But the *classes* (Heads) also include padding?
                    # We should probably mask score for padded heads to -inf.
                    arc_scores.reshape(-1, T),
                    head_targets.view(-1),
                )

                # 3. Rel Loss
                # Need to use Predicted Heads or Gold Heads?
                # Teacher Forcing: Use Gold Heads.
                rel_scores = self.model.decode_rels(
                    output["rel_h"], output["rel_d"], output["rel_U"], head_targets
                )  # (B, T, L)

                rel_loss = rel_criterion(
                    rel_scores.view(-1, rel_scores.shape[-1]), rel_targets.view(-1)
                )

                loss = pos_loss + arc_loss + rel_loss
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            print(
                f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(train_loader):.4f}"
            )

        # Save
        print(f"Saving model to {save_path}...")
        save_dict = {
            "model": self.model.state_dict(),
            "char_vocab": self.dataset.char_vocab,
            "pos_vocab": self.dataset.pos_vocab,
            "deprel_vocab": self.dataset.deprel_vocab,
        }
        torch.save(save_dict, save_path)
        print("Done.")

    def train_morph(
        self,
        corpus_path,
        save_path="neural_morph_model.pt",
        epochs=10,
        batch_size=64,
        lr=1e-3,
    ):
        print(f"Loading SyllableBIODataset from {corpus_path}...")
        self.dataset = SyllableBIODataset(corpus_path, build_vocab=True)

        train_loader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=True,
            collate_fn=collate_fn_morph,
        )

        print("Initializing SyllableMorphModel...")
        num_tags = len(self.dataset.tag_vocab)
        self.model = SyllableMorphModel(
            vocab_size=len(self.dataset.char_vocab),
            embed_dim=128,
            num_heads=4,
            num_layers=2,
            num_tags=num_tags,
            hidden_dim=256,
            dropout=0.1,
        ).to(self.device)

        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss(ignore_index=0)  # Pad

        print(f"Start Morph Training on {self.device} for {epochs} epochs...")

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0

            for batch in train_loader:
                forms = batch["forms"].to(self.device)
                tags = batch["tags"].to(self.device)
                mask = batch["mask"].to(self.device)  # Pad Mask

                optimizer.zero_grad()

                # Output: (B, T, NumTags)
                logits = self.model(forms, mask=mask)

                # Flatten
                loss = criterion(logits.view(-1, num_tags), tags.view(-1))

                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            print(
                f"Epoch {epoch+1}/{epochs} - Morph Loss: {total_loss/len(train_loader):.4f}"
            )

        print(f"Saving morph model to {save_path}...")
        save_dict = {
            "model": self.model.state_dict(),
            "char_vocab": self.dataset.char_vocab,
            "tag_vocab": self.dataset.tag_vocab,
        }
        torch.save(save_dict, save_path)
        print("Done.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", help="Path to corpus file")
    parser.add_argument(
        "--mode", choices=["syntax", "morph"], default="syntax", help="Training mode"
    )
    parser.add_argument("--device", default="cpu", help="Device (cpu/cuda)")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")

    args = parser.parse_args()

    trainer = NeuralTrainer(device=args.device)

    if args.mode == "syntax":
        trainer.train(args.corpus, epochs=args.epochs)
    elif args.mode == "morph":
        trainer.train_morph(args.corpus, epochs=args.epochs)
