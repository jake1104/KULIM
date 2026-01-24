import torch
from torch.utils.data import Dataset
from collections import defaultdict
import glob


class Vocab:
    def __init__(self, items=None, pad_token="<PAD>", unk_token="<UNK>", specials=None):
        self.item2id = {}
        self.id2item = {}
        self.pad_token = pad_token
        self.unk_token = unk_token

        idx = 0
        if pad_token:
            self.item2id[pad_token] = idx
            self.id2item[idx] = pad_token
            idx += 1
        if unk_token:
            self.item2id[unk_token] = idx
            self.id2item[idx] = unk_token
            idx += 1

        if specials:
            for s in specials:
                if s not in self.item2id:
                    self.item2id[s] = idx
                    self.id2item[idx] = s
                    idx += 1

        self.special_count = idx

        if items:
            for item in items:
                if item not in self.item2id:
                    self.item2id[item] = idx
                    self.id2item[idx] = item
                    idx += 1

    def __len__(self):
        return len(self.item2id)

    def __getitem__(self, item):
        return self.item2id.get(item, self.item2id.get(self.unk_token))

    def get_id(self, item):
        return self[item]

    def get_item(self, idx):
        return self.id2item.get(idx, self.unk_token)


class CoNLLUDataset(Dataset):
    def __init__(
        self,
        filepaths,
        char_vocab=None,
        pos_vocab=None,
        deprel_vocab=None,
        build_vocab=False,
    ):
        self.sentences = []
        self.build_vocab = build_vocab

        # Raw data collectors
        all_chars = set()
        all_pos = set()
        all_deprels = set()

        # Load parsing
        from .conllu import ConlluParser

        parser = ConlluParser()

        path_list = glob.glob(filepaths) if "*" in filepaths else [filepaths]

        for path in path_list:
            sents = parser.parse(path)
            for sent in sents:
                # Process Sentence
                tokens = sent["tokens"]
                # Skip invalid
                if not tokens:
                    continue

                # Extract features
                # For Morph Model: We need full raw text (chars) + syllable-aligned tags?
                # Actually, CoNLLU gives us Words. We need to reconstruct chars and align tags.
                # Simplification: Train "Syntax Model" on Words first.
                # "Morph Model" training requires raw character -> POS mapping (e.g. Sejong corpus).
                # CoNLLU usually has segmented words.
                # We will support Syntax Training here primarily (Word -> POS/Dep).

                forms = [t["form"] for t in tokens]
                upos = [t["upos"] for t in tokens]
                heads = [int(t["head"]) for t in tokens]  # 1-based usually
                deprels = [t["deprel"] for t in tokens]

                # Check 0-based indexing
                # CoNLL-U heads are 1-based, 0 is root.
                # Should convert to 0-based for specific tokens, Root is usually special.
                # In Biaffine: Root is often index 0 (explicit <ROOT> token usually added at start).
                # We will prepend <ROOT> to every sentence.

                if build_vocab:
                    all_chars.update(
                        forms
                    )  # Using "Word" as input unit for Syntax Model
                    all_pos.update(upos)
                    all_deprels.update(deprels)

                self.sentences.append(
                    {"forms": forms, "upos": upos, "heads": heads, "deprels": deprels}
                )

        if build_vocab:
            self.char_vocab = Vocab(
                all_chars, pad_token="<PAD>", unk_token="<UNK>", specials=["<ROOT>"]
            )
            self.pos_vocab = Vocab(
                all_pos, pad_token="<PAD>", unk_token="<UNK>", specials=["<ROOT-POS>"]
            )
            self.deprel_vocab = Vocab(
                all_deprels, pad_token="<PAD>", unk_token="<UNK>", specials=["root"]
            )
        else:
            self.char_vocab = char_vocab
            self.pos_vocab = pos_vocab
            self.deprel_vocab = deprel_vocab

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        item = self.sentences[idx]

        # Prepend ROOT
        forms = ["<ROOT>"] + item["forms"]
        upos = ["<ROOT-POS>"] + item["upos"]
        heads = [0] + item["heads"]  # 0 points to nothing/self?
        # If original head was 0 (Root), it should now point to 0 (our <ROOT>)?
        # Original: 1-based index relative to words.
        # Now we added <ROOT> at index 0.
        # If token 1 had head 0 (Root), it now points to 0. Correct.
        # If token 2 had head 1, it now points to 1. Correct.
        deprels = ["root"] + item["deprels"]

        # Convert to IDs
        form_ids = [self.char_vocab[f] for f in forms]
        pos_ids = [self.pos_vocab[p] for p in upos]
        deprel_ids = [self.deprel_vocab[d] for d in deprels]

        return {
            "form_ids": torch.tensor(form_ids, dtype=torch.long),
            "pos_ids": torch.tensor(pos_ids, dtype=torch.long),
            "head_ids": torch.tensor(heads, dtype=torch.long),
            "deprel_ids": torch.tensor(deprel_ids, dtype=torch.long),
            "length": len(form_ids),
        }


def collate_fn(batch):
    # Padding
    max_len = max(item["length"] for item in batch)

    B = len(batch)
    form_batch = torch.zeros(B, max_len, dtype=torch.long)
    pos_batch = torch.zeros(B, max_len, dtype=torch.long)
    head_batch = torch.zeros(B, max_len, dtype=torch.long)
    deprel_batch = torch.zeros(B, max_len, dtype=torch.long)
    mask_batch = torch.zeros(
        B, max_len, dtype=torch.bool
    )  # True for padding in nn.Transformer usually?
    # PyTorch Transformer: src_key_padding_mask: (B, S) True for ignored positions

    # Initialize with padding values if needed, typically 0
    # form_batch.fill_(0)

    for i, item in enumerate(batch):
        L = item["length"]
        form_batch[i, :L] = item["form_ids"]
        pos_batch[i, :L] = item["pos_ids"]
        head_batch[i, :L] = item["head_ids"]
        deprel_batch[i, :L] = item["deprel_ids"]
        mask_batch[i, L:] = True  # Masked positions

    return {
        "forms": form_batch,
        "pos": pos_batch,
        "heads": head_batch,
        "deprels": deprel_batch,
        "mask": mask_batch,
    }


class SyllableBIODataset(Dataset):
    """
    Dataset for Syllable-level Morphological Analysis (BIO Tagging)
    Input: "인간은" (Syllables)
    Output: ["B-NNG", "I-NNG", "B-JX"] (Tags)
    """

    def __init__(
        self,
        filepaths,
        char_vocab=None,
        tag_vocab=None,
        build_vocab=False,
    ):
        self.samples = []
        self.build_vocab = build_vocab

        # Raw data collectors
        all_chars = set()
        all_tags = set()

        from .conllu import ConlluParser

        parser = ConlluParser()
        path_list = glob.glob(filepaths) if "*" in filepaths else [filepaths]

        for path in path_list:
            sents = parser.parse(path)
            for sent in sents:
                tokens = sent["tokens"]
                if not tokens:
                    continue

                for token in tokens:
                    form = token["form"]
                    morphs = token["morphs"]

                    if not form or not morphs:
                        continue

                    # Alignment Logic
                    # Filter spaces in form (sometimes CoNLL forms have spaces?) -> Usually Eojeol has no space.

                    # reconstruct form from morphs to check alignment
                    recon = "".join(m[0] for m in morphs)

                    if form != recon:
                        # Mismatch case (restoration happened, e.g. "했다" -> "하+었+다")
                        # For now, SKIP these complex cases for training stability.
                        # We only train on 1:1 mappings.
                        continue

                    # Generate Tags
                    tags = []
                    current_len = 0
                    for diff_idx, (m_surf, m_pos) in enumerate(morphs):
                        m_len = len(m_surf)
                        if m_len == 0:
                            continue

                        # BIO Tagging
                        # "B-POS" for first char, "I-POS" for rest
                        tags.append(f"B-{m_pos}")
                        for _ in range(m_len - 1):
                            tags.append(f"I-{m_pos}")

                    chars = list(form)

                    if len(chars) != len(tags):
                        # Should not happen if recon == form
                        continue

                    if build_vocab:
                        all_chars.update(chars)
                        all_tags.update(tags)

                    self.samples.append({"chars": chars, "tags": tags})

        if build_vocab:
            self.char_vocab = Vocab(
                all_chars,
                pad_token="<PAD>",
                unk_token="<UNK>",
                specials=["<S>", "</S>"],
            )
            self.tag_vocab = Vocab(all_tags, pad_token="<PAD>", unk_token="<UNK>")
        else:
            self.char_vocab = char_vocab
            self.tag_vocab = tag_vocab

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]

        # Add Start/End tokens? Not strictly needed for BERT-like tagging but helpful for margins
        chars = item["chars"]
        tags = item["tags"]

        form_ids = [self.char_vocab[c] for c in chars]
        tag_ids = [self.tag_vocab[t] for t in tags]

        return {
            "form_ids": torch.tensor(form_ids, dtype=torch.long),
            "tag_ids": torch.tensor(tag_ids, dtype=torch.long),
            "length": len(form_ids),
        }


def collate_fn_morph(batch):
    # Padding per batch
    max_len = max(item["length"] for item in batch)
    B = len(batch)

    form_batch = torch.zeros(B, max_len, dtype=torch.long)
    tag_batch = torch.zeros(B, max_len, dtype=torch.long)
    mask_batch = torch.zeros(B, max_len, dtype=torch.bool)  # True for padding

    for i, item in enumerate(batch):
        L = item["length"]
        form_batch[i, :L] = item["form_ids"]
        tag_batch[i, :L] = item["tag_ids"]
        mask_batch[i, L:] = True

    return {"forms": form_batch, "tags": tag_batch, "mask": mask_batch}
