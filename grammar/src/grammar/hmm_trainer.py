import json
import math
import re
from collections import defaultdict, Counter
from typing import Dict, Tuple, Optional, List


class HMMTrainer:
    def __init__(self):
        self.transition_counts = defaultdict(lambda: defaultdict(int))
        self.emission_counts = defaultdict(lambda: defaultdict(int))
        self.pos_counts = defaultdict(int)
        self.suffix_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        self.total_transitions = 0
        self.vocab_size = 0
        self.unk_suffix_probs = {}

        self.POS_PRIORS = {
            "NNG": 0.25, "NNP": 0.05, "NNB": 0.03, "NP": 0.02, "NR": 0.01,
            "VV": 0.08, "VA": 0.05, "VX": 0.02, "VCP": 0.02, "VCN": 0.01,
            "MM": 0.03, "MAG": 0.05, "IC": 0.01,
            "JKS": 0.04, "JKO": 0.03, "JKG": 0.02, "JKB": 0.04,
            "JKV": 0.01, "JC": 0.01, "JX": 0.03,
            "EP": 0.04, "EF": 0.05, "EC": 0.05, "ETM": 0.02, "ETN": 0.01,
            "XPN": 0.01, "XSN": 0.01, "XSV": 0.01, "XSA": 0.01,
            "SF": 0.01, "SP": 0.01,
        }

    def train(self, corpus_path, encoding="utf-8"):
        print(f"Training HMM from {corpus_path}...")
        sentence_count = 0

        with open(corpus_path, "r", encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                tokens = self._parse_line(line)
                if not tokens:
                    continue

                prev_pos = "START"
                for word, pos in tokens:
                    self.transition_counts[prev_pos][pos] += 1
                    self.emission_counts[pos][word] += 1
                    self.pos_counts[pos] += 1

                    self._learn_suffix_features(word, pos)

                    prev_pos = pos

                self.transition_counts[prev_pos]["END"] += 1
                sentence_count += 1

        self.vocab_size = sum(
            len(self.emission_counts[pos]) for pos in self.emission_counts
        )

        self._build_unk_model()

        print(f"  Sentences: {sentence_count}")
        print(f"  Unique POS tags: {len(self.pos_counts)}")
        print(f"  Unique words: {self.vocab_size}")
        print("Training complete.")

    def train_from_morphs(self, sentences):
        for words, pos_tags in sentences:
            prev_pos = "START"
            for word, pos in zip(words, pos_tags):
                self.transition_counts[prev_pos][pos] += 1
                self.emission_counts[pos][word] += 1
                self.pos_counts[pos] += 1
                self._learn_suffix_features(word, pos)
                prev_pos = pos
            self.transition_counts[prev_pos]["END"] += 1

        self.vocab_size = sum(
            len(self.emission_counts[pos]) for pos in self.emission_counts
        )
        self._build_unk_model()

    def _parse_line(self, line):
        if " + " in line:
            parts = line.split(" + ")
        elif "\t" in line:
            parts = line.split("\t")
        else:
            parts = [line]

        tokens = []
        for part in parts:
            part = part.strip()
            if "/" in part:
                word, pos = part.rsplit("/", 1)
                tokens.append((word.strip(), pos.strip()))
        return tokens

    def _learn_suffix_features(self, word, pos):
        for length in range(1, min(4, len(word) + 1)):
            suffix = word[-length:]
            self.suffix_counts[pos][suffix][f"len{length}"] += 1

    def _build_unk_model(self):
        for pos in self.pos_counts:
            total = sum(self.suffix_counts[pos][s].values() for s in self.suffix_counts[pos])
            if total == 0:
                continue
            for suffix in self.suffix_counts[pos]:
                for key, count in self.suffix_counts[pos][suffix].items():
                    prob = count / total
                    self.suffix_counts[pos][suffix][key] = prob

    def _suffix_prob(self, word, pos):
        if not word:
            return 0.0

        prob = 0.0
        for length in range(1, min(4, len(word) + 1)):
            suffix = word[-length:]
            if suffix in self.suffix_counts.get(pos, {}):
                prob += self.suffix_counts[pos][suffix].get(f"len{length}", 0) * 0.5
        return prob

    def emission_prob(self, word, pos, lambda_ml=0.6, lambda_suffix=0.3, lambda_unk=0.1):
        total = sum(self.emission_counts[pos].values())
        if total == 0:
            total = 1

        ml_prob = self.emission_counts[pos].get(word, 0) / total

        suffix_prob = self._suffix_prob(word, pos) * 0.5

        char_prob = 0.0
        hangeul_len = sum(1 for c in word if "가" <= c <= "힣")
        if pos.startswith("N") and hangeul_len >= 2:
            char_prob = 0.05
        elif pos.startswith("V") and word.endswith("다"):
            char_prob = 0.03
        elif pos.startswith("E") and len(word) <= 3:
            char_prob = 0.04
        elif pos.startswith("J") and len(word) <= 2:
            char_prob = 0.04

        return lambda_ml * ml_prob + lambda_suffix * suffix_prob + lambda_unk * char_prob

    def save_model(self, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pos_list = list(self.pos_counts.keys())
        all_tags = pos_list + ["START", "END"]

        model = {
            "transition": {},
            "emission": {},
            "suffix": {},
            "pos_list": pos_list,
            "vocab_size": self.vocab_size,
            "pos_priors": {p: self.POS_PRIORS.get(p, 0.01) for p in pos_list},
        }

        k = 0.01
        for prev in all_tags:
            total = sum(self.transition_counts[prev].values())
            denom = total + k * len(all_tags)
            if denom == 0:
                continue

            model["transition"][prev] = {}
            for curr in all_tags:
                count = self.transition_counts[prev][curr]
                prob = (count + k) / denom
                model["transition"][prev][curr] = math.log(prob)

        for pos in self.pos_counts:
            total = sum(self.emission_counts[pos].values())
            denom = total + k * 10000

            model["emission"][pos] = {}
            for word, count in self.emission_counts[pos].items():
                prob = (count + k) / denom
                model["emission"][pos][word] = math.log(prob)

            model["emission"][pos]["__UNK__"] = math.log(k / denom)

        for pos in self.pos_counts:
            model["suffix"][pos] = dict(self.suffix_counts.get(pos, {}))

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(model, f, ensure_ascii=False, indent=2)

        print(f"Model saved to {output_path}")

    def load_model(self, path):
        pass


import os
