
import json
import math
from collections import defaultdict
import os


class HMMTrainer:
    def __init__(self):
        self.transition_counts = defaultdict(lambda: defaultdict(int))
        self.emission_counts = defaultdict(lambda: defaultdict(int))
        self.pos_counts = defaultdict(int)
        self.total_transitions = 0

    def train(self, corpus_path):
        print(f"Training HMM from {corpus_path}...")

        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # "친구/NNG + 가/JKS" -> [("친구", "NNG"), ("가", "JKS")]
                tokens = []
                parts = line.split(" + ")
                for part in parts:
                    if "/" in part:
                        word, pos = part.rsplit("/", 1)
                        tokens.append((word, pos))

                # Count transitions and emissions
                prev_pos = "START"
                for word, pos in tokens:
                    self.transition_counts[prev_pos][pos] += 1
                    self.emission_counts[pos][word] += 1
                    self.pos_counts[pos] += 1
                    prev_pos = pos

                self.transition_counts[prev_pos]["END"] += 1

        print("Training complete.")
        print(f"  Unique POS tags: {len(self.pos_counts)}")

    def save_model(self, output_path):
        model = {
            "transition": {},
            "emission": {},
            "pos_list": list(self.pos_counts.keys()),
        }

        # Calculate probabilities with smoothing
        k = 0.1  # Add-k smoothing

        # Transition Probabilities
        all_tags = list(self.pos_counts.keys()) + ["START", "END"]
        for prev in all_tags:
            total = sum(self.transition_counts[prev].values()) + (k * len(all_tags))
            if total == 0:
                continue

            model["transition"][prev] = {}
            for curr in all_tags:
                count = self.transition_counts[prev][curr]
                prob = (count + k) / total
                model["transition"][prev][curr] = prob

        # Emission Probabilities
        # Emission은 단어 수가 너무 많으므로, 파일 크기를 줄이기 위해
        # 자주 등장하는 단어만 저장하거나,
        # 실행 시점에 dictionary.csv를 참조하여 계산하는 방식이 나을 수 있음.
        # 하지만 여기서는 일단 저장. (단어 수가 2000개 정도라 괜찮음)
        for pos in self.pos_counts:
            total = (
                sum(self.emission_counts[pos].values()) + k * 10000
            )  # Vocabulary size approx

            model["emission"][pos] = {}
            for word, count in self.emission_counts[pos].items():
                prob = (count + k) / total
                model["emission"][pos][word] = prob

            # Unknown word probability for this POS
            model["emission"][pos]["__UNK__"] = k / total

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(model, f, ensure_ascii=False, indent=2)

        print(f"Model saved to {output_path}")


if __name__ == "__main__":
    trainer = HMMTrainer()
    trainer.train("grammar/beta/v04/data/corpus.txt")
    trainer.save_model("grammar/beta/v04/data/hmm_model.json")
