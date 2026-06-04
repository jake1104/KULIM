from typing import List, Tuple, Set


class ConstraintValidator:
    """형태소 분석 제약 조건 검사기"""

    def __init__(self):
        # 불가능한 품사 연속 (Prev -> Curr)
        self.impossible_transitions: Set[Tuple[str, str]] = {
            # 동일 조사 연속 불가
            ("JKS", "JKS"), ("JKO", "JKO"), ("JKG", "JKG"),
            ("JKB", "JKB"), ("JX", "JX"), ("JC", "JC"),
            # 종결어미 뒤에 조사/어미 불가
            ("EF", "JKS"), ("EF", "JKO"), ("EF", "JKG"),
            ("EF", "JKB"), ("EF", "JX"), ("EF", "JC"),
            ("EF", "EF"), ("EF", "EC"), ("EF", "EP"),
            ("EF", "ETM"), ("EF", "ETN"),
            # 문장부호 뒤에 조사 불가
            ("SF", "JKS"), ("SF", "JKO"), ("SF", "JKG"),
            ("SF", "JKB"), ("SF", "JX"),
            ("SF", "EC"), ("SF", "EF"), ("SF", "EP"),
            # 선어말어미 뒤에 주격/목적격 불가
            ("EP", "JKS"), ("EP", "JKO"), ("EP", "JKG"),
            # 관형격조사 뒤에 조사 불가
            ("JKG", "JKS"), ("JKG", "JKO"), ("JKG", "JX"),
            # 보조사 뒤에 주격/목적격/관형격 불가
            ("JX", "JKS"), ("JX", "JKO"), ("JX", "JKG"),
            # 접속조사 뒤에 조사 불가
            ("JC", "JKS"), ("JC", "JKO"), ("JC", "JKG"),
            # 명사형 전성어미 뒤에 조사만 가능 (어미 불가)
            ("ETN", "EF"), ("ETN", "EC"), ("ETN", "EP"),
            ("ETN", "ETM"), ("ETN", "ETN"),
            # 관형형 전성어미 뒤에 조사 불가
            ("ETM", "JKS"), ("ETM", "JKO"), ("ETM", "JKG"),
            ("ETM", "JX"), ("ETM", "JC"),
            # 조사 뒤에 접두사/어근 불가
            ("JKS", "XPN"), ("JKO", "XPN"),
            ("JKB", "XPN"), ("JKG", "XPN"),
            # 종결어미 뒤에 동사/형용사 불가 (새 문장이 시작되어야 함)
            ("EF", "VV"), ("EF", "VA"), ("EF", "VX"),
            ("EF", "VCP"), ("EF", "VCN"),
            # 보조용언(VX) 뒤에 조사 불가
            ("VX", "JKS"), ("VX", "JKO"), ("VX", "JKG"),
            ("VX", "JKB"), ("VX", "JX"),
            # 감탄사 뒤에 조사 불가
            ("IC", "JKO"), ("IC", "JKG"),
            # 명사 뒤에 바로 선어말어미 불가
            ("NNG", "EP"), ("NNP", "EP"), ("NNB", "EP"),
            ("NP", "EP"), ("NR", "EP"),
            # 주격 뒤에 또 주격 불가
            ("JKS", "JKO"),
            # 용언 뒤에 관형격/부사격조사 불가 (명사형 전성만 가능)
            ("VV", "JKS"), ("VV", "JKO"), ("VV", "JKG"),
            ("VV", "JKB"), ("VV", "JX"), ("VV", "JC"),
            ("VA", "JKS"), ("VA", "JKO"), ("VA", "JKG"),
            ("VA", "JKB"), ("VA", "JX"), ("VA", "JC"),
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
