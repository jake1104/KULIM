from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
import json


@dataclass
class TransitionModel:
    """학습 가능한 전이 확률 모델 (HMM Style)"""

    # P(Current | Previous)
    # Key: (PrevPOS, CurrPOS), Value: log_prob (cost)
    transitions: Dict[str, float] = field(default_factory=dict)

    # Emission/Observation probabilities could be here or in dictionary
    # For now, we focus on transitions.

    def get_transition_cost(self, prev_pos: Optional[str], curr_pos: str) -> float:
        if prev_pos is None:
            return 0.0  # Start

        # 1. Look for specific transition
        key = f"{prev_pos},{curr_pos}"
        if key in self.transitions:
            return self.transitions[key]

        # 2. Backoff / Default Rules (Heuristics as Priors)
        # These correspond to the old BONUS constants.
        # Bonus X -> Cost -X

        # Noun + Josa
        if prev_pos.startswith("N") and curr_pos.startswith("J"):
            return -25.0  # BONUS_NOUN_JOSA

        # Josa + Noun (e.g., 에 + 집)
        if prev_pos.startswith("J") and curr_pos.startswith("N"):
            return -10.0

        # Verb/Adj + Eomi
        if prev_pos.startswith("V") and curr_pos.startswith("E"):
            return -20.0  # BONUS_VERB_EOMI

        # Eomi + Eomi (연결어미 + 보조사/어미)
        if prev_pos.startswith("E") and curr_pos.startswith("E"):
            return -12.0  # BONUS_EOMI_EOMI

        # Eomi + Josa (e.g., 기 + 에)
        if prev_pos == "ETN" and curr_pos.startswith("J"):
            return -15.0

        # Adverb + Noun
        if prev_pos == "MAG" and curr_pos.startswith("N"):
            return -18.0  # BONUS_ADVERB_NOUN

        # Adverb + Verb
        if prev_pos == "MAG" and curr_pos.startswith("V"):
            return -12.0  # BONUS_ADVERB_VERB

        # Determiner + Noun
        if prev_pos == "MM" and curr_pos.startswith("N"):
            return -15.0  # BONUS_DETERMINER_NOUN

        # Noun + Verb (명사+하다/되다 등)
        if prev_pos.startswith("N") and curr_pos.startswith("V"):
            return -8.0

        # Noun + Copula (N + 이다/아니다)
        if prev_pos.startswith("N") and curr_pos in ("VCP", "VCN"):
            return -15.0

        # Copula + Eomi
        if prev_pos in ("VCP", "VCN") and curr_pos.startswith("E"):
            return -15.0

        # Number + Noun (수사+명사)
        if prev_pos == "NR" and curr_pos.startswith("N"):
            return -10.0

        # Number + Number
        if prev_pos == "NR" and curr_pos == "NR":
            return -15.0

        # Noun + Noun (합성명사)
        if prev_pos.startswith("N") and curr_pos.startswith("N"):
            return -12.0

        # Interjection + Josa
        if prev_pos == "IC" and curr_pos.startswith("J"):
            return -10.0

        # Affix + Eomi (XSV/XSA/.. + Eomi)
        if prev_pos.startswith("X") and curr_pos.startswith("E"):
            return -15.0

        # Affix + Josa (XSN + Josa)
        if prev_pos.startswith("XS") and curr_pos.startswith("J"):
            return -15.0

        # Prefix + Noun (XPN + NNG)
        if prev_pos == "XPN" and curr_pos.startswith("N"):
            return -12.0

        # Auxiliary verb + Eomi (VX + E)
        if prev_pos == "VX" and curr_pos.startswith("E"):
            return -12.0

        # Eomi + Auxiliary (E + VX)
        if prev_pos.startswith("E") and curr_pos == "VX":
            return -8.0

        # Auxiliary + Auxiliary
        if prev_pos == "VX" and curr_pos == "VX":
            return -10.0

        # Final ending + anything (high penalty - should be sentence end)
        if prev_pos == "EF":
            if curr_pos.startswith("S"):
                return 0.0
            return 25.0

        # 3. Default Penalty
        return 15.0

    def train(self, transitions: Dict[str, float]):
        self.transitions = transitions

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.transitions, f, indent=2)

    def load(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.transitions = json.load(f)


@dataclass
class ScoringConfig:
    """Scoring configuration wrapping learned model"""

    # Model
    model: TransitionModel = field(default_factory=TransitionModel)

    # Base Costs (still useful as priors or for OOV)
    COST_LONG_WORD: float = -40.0
    COST_MEDIUM_WORD: float = -30.0
    COST_SHORT_WORD: float = -5.0

    COST_OOV: float = 30.0

    # Bonuses/Penalties (Backward Compat + Heuristics)
    PENALTY_SINGLE_VERB_IC: float = 20.0
    BONUS_NOUN_2PLUS: float = 5.0
    BONUS_ADVERB_2PLUS: float = 10.0

    # Context Bonuses (Legacy - specific values for stemmer if not using model)
    # Ideally should be removed but stemmer.py references them.
    # We will keep them but encourage get_transition_cost.
    BONUS_NOUN_JOSA: float = 20.0
    BONUS_VERB_EOMI: float = 15.0
    BONUS_EOMI_EOMI: float = 10.0
    BONUS_ADVERB_NOUN: float = 15.0
    BONUS_ADVERB_VERB: float = 10.0
    BONUS_DETERMINER_NOUN: float = 10.0

    # Conjugation
    COST_CONJUGATION_BASE: float = -25.0
    BONUS_CONJ_CONTEXT: float = 10.0

    def get_length_cost(self, length: int) -> float:
        if length >= 3:
            return self.COST_LONG_WORD
        elif length == 2:
            return self.COST_MEDIUM_WORD
        return self.COST_SHORT_WORD

    def get_transition_cost(self, prev: Optional[str], curr: str) -> float:
        return self.model.get_transition_cost(prev, curr)


# Global Instance
SCORING = ScoringConfig()
