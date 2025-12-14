from typing import List, Tuple, Set


class ConstraintValidator:
    """형태소 분석 제약 조건 검사기"""

    def __init__(self):
        # 불가능한 품사 연속 (Prev -> Curr)
        self.impossible_transitions: Set[Tuple[str, str]] = {
            ("JKS", "JKS"),  # 주격조사 + 주격조사
            ("JKO", "JKO"),  # 목적격조사 + 목적격조사
            ("EF", "JKS"),  # 종결어미 + 주격조사 (문장이 끝났는데 조사가 옴)
            ("EF", "JKO"),
            ("EF", "EF"),  # 종결어미 + 종결어미
            ("SF", "JKS"),  # 마침표 + 조사
        }

    def is_valid_transition(self, prev_pos: str, curr_pos: str) -> bool:
        if (prev_pos, curr_pos) in self.impossible_transitions:
            return False
        return True

    def validate_sequence(self, morphemes: List[Tuple[str, str]]) -> bool:
        for i in range(1, len(morphemes)):
            prev = morphemes[i - 1][1]
            curr = morphemes[i][1]
            if not self.is_valid_transition(prev, curr):
                return False
        return True
