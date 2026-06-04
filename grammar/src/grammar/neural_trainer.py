import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, SubsetRandomSampler
import os
import math
import json
from .model import SimpleTagger
from .dataset import CoNLLUDataset, collate_fn, SyllableBIODataset, collate_fn_morph


class EarlyStopping:
    def __init__(self, patience=5, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.counter = 0
        self.best_model = None

    def step(self, loss, model):
        if loss < self.best_loss - self.min_delta:
            self.best_loss = loss
            self.best_model = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            self.counter = 0
            return False
        self.counter += 1
        return self.counter >= self.patience


class NeuralTrainer:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = None
        self.dataset = None

    def _init_syntax_model(self, vocab_size, pos_vocab_size, deprel_vocab_size):
        try:
            from .model import CombinedTransformerBiaffine
            print("  Using CombinedTransformerBiaffine (full parser)")
            return CombinedTransformerBiaffine(
                vocab_size=vocab_size, embed_dim=128, enc_heads=4,
                enc_layers=2, pos_vocab_size=pos_vocab_size,
                num_rels=deprel_vocab_size, hidden_dim=128, lstm_layers=1,
            )
        except ImportError:
            print("  Falling back to SimpleTagger (POS only)")
            return SimpleTagger(vocab_size=vocab_size, pos_vocab_size=pos_vocab_size)

    def train(
        self, corpus_path, save_path="neural_model.pt",
        epochs=10, batch_size=32, lr=1e-3, warmup=0.1, weight_decay=1e-5,
        clip_grad=5.0, early_stop_patience=5, k_fold=0, verbose=True,
    ):
        if verbose:
            print(f"Loading dataset from {corpus_path}...")
        self.dataset = CoNLLUDataset(corpus_path, build_vocab=True)

        dataset_size = len(self.dataset)
        indices = list(range(dataset_size))

        if k_fold > 0:
            fold_size = dataset_size // k_fold
            for fold in range(k_fold):
                if verbose:
                    print(f"\n{'='*50}")
                    print(f"Fold {fold+1}/{k_fold}")
                    print(f"{'='*50}")
                val_indices = indices[fold * fold_size:(fold + 1) * fold_size]
                train_indices = indices[:fold * fold_size] + indices[(fold + 1) * fold_size:]
                self._run_training(
                    corpus_path, train_indices, val_indices,
                    save_path, epochs, batch_size, lr, warmup,
                    weight_decay, clip_grad, early_stop_patience, verbose,
                    fold=fold,
                )
        else:
            train_size = int(0.9 * dataset_size)
            train_indices = indices[:train_size]
            val_indices = indices[train_size:]
            self._run_training(
                corpus_path, train_indices, val_indices,
                save_path, epochs, batch_size, lr, warmup,
                weight_decay, clip_grad, early_stop_patience, verbose,
            )

    def _run_training(self, corpus_path, train_indices, val_indices,
                      save_path, epochs, batch_size, lr, warmup,
                      weight_decay, clip_grad, early_stop_patience, verbose,
                      fold=None):
        train_sampler = SubsetRandomSampler(train_indices)
        val_sampler = SubsetRandomSampler(val_indices)

        train_loader = DataLoader(
            self.dataset, batch_size=batch_size, sampler=train_sampler,
            collate_fn=collate_fn, num_workers=0, pin_memory=True,
        )
        val_loader = DataLoader(
            self.dataset, batch_size=batch_size, sampler=val_sampler,
            collate_fn=collate_fn, num_workers=0,
        )

        vocab_size = len(self.dataset.char_vocab)
        pos_vocab_size = len(self.dataset.pos_vocab)
        deprel_vocab_size = len(self.dataset.deprel_vocab)

        self.model = self._init_syntax_model(vocab_size, pos_vocab_size, deprel_vocab_size).to(self.device)

        optimizer = optim.AdamW(
            self.model.parameters(), lr=lr, weight_decay=weight_decay,
        )

        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=len(train_loader) * 2, T_mult=2, eta_min=lr * 0.01,
        )

        pos_criterion = nn.CrossEntropyLoss(ignore_index=0)
        early_stop = EarlyStopping(patience=early_stop_patience)

        total_steps = len(train_loader) * epochs
        warmup_steps = int(total_steps * warmup)

        if verbose:
            print(f"  Model params: {sum(p.numel() for p in self.model.parameters()):,}")
            print(f"  Train: {len(train_indices)}, Val: {len(val_indices)}")
            print(f"  Start training on {self.device}...")

        for epoch in range(epochs):
            self.model.train()
            total_loss = total_pos_loss = 0

            for step, batch in enumerate(train_loader):
                forms = batch["forms"].to(self.device, non_blocking=True)
                pos_targets = batch["pos"].to(self.device, non_blocking=True)
                mask = batch["mask"].to(self.device, non_blocking=True)

                global_step = epoch * len(train_loader) + step
                if global_step < warmup_steps:
                    for g in optimizer.param_groups:
                        g['lr'] = lr * (global_step + 1) / warmup_steps

                optimizer.zero_grad(set_to_none=True)

                if hasattr(self.model, 'biaffine') or hasattr(self.model, 'encoder'):
                    head_targets = batch["heads"].to(self.device, non_blocking=True)
                    rel_targets = batch["deprels"].to(self.device, non_blocking=True)
                    output = self.model(forms, mask=mask)

                    pos_loss = pos_criterion(
                        output["pos_logits"].view(-1, output["pos_logits"].shape[-1]),
                        pos_targets.view(-1),
                    )

                    arc_scores = output["arc_scores"].transpose(1, 2)
                    B, T = arc_scores.shape[:2]
                    arc_loss = pos_criterion(
                        arc_scores.reshape(-1, T), head_targets.view(-1),
                    )

                    try:
                        rel_scores = self.model.decode_rels(
                            output["rel_h"], output["rel_d"], output["rel_U"], head_targets
                        )
                        rel_loss = nn.CrossEntropyLoss(ignore_index=0)(
                            rel_scores.view(-1, rel_scores.shape[-1]), rel_targets.view(-1),
                        )
                    except Exception:
                        rel_loss = torch.tensor(0.0, device=self.device)

                    loss = pos_loss + arc_loss + rel_loss
                else:
                    logits = self.model(forms, mask=mask)
                    loss = pos_criterion(logits.view(-1, pos_vocab_size), pos_targets.view(-1))
                    pos_loss = loss
                    arc_loss = torch.tensor(0.0, device=self.device)

                loss.backward()
                if clip_grad > 0:
                    nn.utils.clip_grad_norm_(self.model.parameters(), clip_grad)
                optimizer.step()

                total_loss += loss.item()
                total_pos_loss += pos_loss.item()

            avg_loss = total_loss / len(train_loader)
            scheduler.step()
            current_lr = optimizer.param_groups[0]['lr']

            val_loss = self._validate(val_loader, pos_criterion, pos_vocab_size)
            should_stop = early_stop.step(val_loss, self.model)

            if verbose:
                print(
                    f"  Epoch {epoch+1}/{epochs} - "
                    f"Loss: {avg_loss:.4f} | Pos: {total_pos_loss/len(train_loader):.4f} | "
                    f"Val: {val_loss:.4f} | LR: {current_lr:.2e}"
                    f"{' [STOP]' if should_stop else ''}"
                )

            if should_stop:
                if verbose:
                    print(f"  Early stopping triggered. Best val loss: {early_stop.best_loss:.4f}")
                self.model.load_state_dict(early_stop.best_model)
                break

        fold_suffix = f"_fold{fold+1}" if fold is not None else ""
        actual_save = save_path.replace('.pt', f'{fold_suffix}.pt') if fold is not None else save_path

        if verbose:
            print(f"Saving model to {actual_save}...")
        os.makedirs(os.path.dirname(actual_save) if os.path.dirname(actual_save) else '.', exist_ok=True)
        self._save_model(actual_save)

    def _validate(self, val_loader, criterion, pos_vocab_size):
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                forms = batch["forms"].to(self.device)
                pos_targets = batch["pos"].to(self.device)
                mask = batch["mask"].to(self.device)

                if hasattr(self.model, 'biaffine') or hasattr(self.model, 'encoder'):
                    head_targets = batch["heads"].to(self.device)
                    output = self.model(forms, mask=mask)
                    pos_loss = criterion(
                        output["pos_logits"].view(-1, output["pos_logits"].shape[-1]),
                        pos_targets.view(-1),
                    )
                else:
                    logits = self.model(forms, mask=mask)
                    pos_loss = criterion(logits.view(-1, pos_vocab_size), pos_targets.view(-1))

                total_loss += pos_loss.item()
        return total_loss / len(val_loader)

    def _save_model(self, path):
        save_dict = {
            "model": self.model.state_dict(),
            "char_vocab": self.dataset.char_vocab,
            "pos_vocab": self.dataset.pos_vocab,
            "deprel_vocab": self.dataset.deprel_vocab,
            "model_config": {
                "type": type(self.model).__name__,
                "pos_vocab_size": len(self.dataset.pos_vocab),
            },
        }
        torch.save(save_dict, path)

    def train_morph(
        self, corpus_path, save_path="neural_morph_model.pt",
        epochs=10, batch_size=64, lr=1e-3, early_stop_patience=5, verbose=True,
    ):
        if verbose:
            print(f"Loading SyllableBIODataset from {corpus_path}...")
        self.dataset = SyllableBIODataset(corpus_path, build_vocab=True)

        dataset_size = len(self.dataset)
        train_size = int(0.9 * dataset_size)
        indices = list(range(dataset_size))

        train_sampler = SubsetRandomSampler(indices[:train_size])
        val_sampler = SubsetRandomSampler(indices[train_size:])

        train_loader = DataLoader(
            self.dataset, batch_size=batch_size, sampler=train_sampler,
            collate_fn=collate_fn_morph, num_workers=0,
        )
        val_loader = DataLoader(
            self.dataset, batch_size=batch_size, sampler=val_sampler,
            collate_fn=collate_fn_morph, num_workers=0,
        )

        num_tags = len(self.dataset.tag_vocab)
        from .model import SyllableMorphModel

        self.model = SyllableMorphModel(
            vocab_size=len(self.dataset.char_vocab), num_tags=num_tags,
        ).to(self.device)

        optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=lr * 0.01)
        criterion = nn.CrossEntropyLoss(ignore_index=0)
        early_stop = EarlyStopping(patience=early_stop_patience)

        if verbose:
            print(f"  Model params: {sum(p.numel() for p in self.model.parameters()):,}")
            print(f"  Tags: {num_tags}, Vocab: {len(self.dataset.char_vocab)}")
            print(f"  Train: {train_size}, Val: {dataset_size - train_size}")

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0

            for batch in train_loader:
                forms = batch["forms"].to(self.device)
                tags = batch["tags"].to(self.device)
                mask = batch["mask"].to(self.device)

                optimizer.zero_grad()
                logits = self.model(forms, mask=mask)
                loss = criterion(logits.view(-1, num_tags), tags.view(-1))
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), 5.0)
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(train_loader)
            scheduler.step()

            val_loss = self._validate_morph(val_loader, criterion, num_tags)
            should_stop = early_stop.step(val_loss, self.model)

            if verbose:
                print(
                    f"  Epoch {epoch+1}/{epochs} - "
                    f"Loss: {avg_loss:.4f} | Val: {val_loss:.4f}"
                    f"{' [STOP]' if should_stop else ''}"
                )

            if should_stop:
                self.model.load_state_dict(early_stop.best_model)
                break

        if verbose:
            print(f"Saving morph model to {save_path}...")
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        save_dict = {
            "model": self.model.state_dict(),
            "char_vocab": self.dataset.char_vocab,
            "tag_vocab": self.dataset.tag_vocab,
        }
        torch.save(save_dict, save_path)

    def _validate_morph(self, val_loader, criterion, num_tags):
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                forms = batch["forms"].to(self.device)
                tags = batch["tags"].to(self.device)
                mask = batch["mask"].to(self.device)
                logits = self.model(forms, mask=mask)
                loss = criterion(logits.view(-1, num_tags), tags.view(-1))
                total_loss += loss.item()
        return total_loss / len(val_loader)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", help="Path to corpus file")
    parser.add_argument("--mode", choices=["syntax", "morph"], default="syntax")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--k-fold", type=int, default=0)
    parser.add_argument("--save", default=None)

    args = parser.parse_args()

    trainer = NeuralTrainer(device=args.device)

    if args.mode == "syntax":
        trainer.train(
            args.corpus, epochs=args.epochs, batch_size=args.batch_size,
            lr=args.lr, k_fold=args.k_fold,
            save_path=args.save or "neural_model.pt",
        )
    elif args.mode == "morph":
        trainer.train_morph(
            args.corpus, epochs=args.epochs, batch_size=args.batch_size,
            lr=args.lr,
            save_path=args.save or "neural_morph_model.pt",
        )
