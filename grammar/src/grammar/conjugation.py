
from typing import List, Tuple, Optional

try:
    from .irregular import IrregularConjugation
except ImportError:
    from irregular import IrregularConjugation

from hangul import compose, decompose

class ConjugationAnalyzer:
    """활용형 분석기 - 축약형 복원 강화"""

    def __init__(self, trie=None):
        self.trie = trie
        self.irregular = IrregularConjugation()

    def restore_verb_stem(self, conjugated: str) -> List[Tuple[str, str]]:
        """
        활용형 복원 (축약형 강화!)

        '갔' → ('가', '았')
        '먹었' → ('먹', '었')
        '좋았' → ('좋', '았')

        Returns:
            [(어간, 어미), ...]
        """
        if not conjugated:
            return []

        results = []

        # 1. 불규칙 먼저
        irr_result = self.irregular.restore_any(conjugated)
        if irr_result:
            stem, ending, irr_type = irr_result
            results.append((stem, ending))

        # 2. 축약형 복원 (핵심!)
        last_char = conjugated[-1]
        cho, jung, jong = decompose(last_char)

        if cho is None:
            return results if results else [(conjugated, "")]

        # 2.1. 종성 'ㅆ' → 과거형 (았/었)
        if jong == "ㅆ":
            base_char = compose(cho, jung, " ")
            if base_char:
                # 모음 조화
                if jung in ["ㅏ", "ㅗ", "ㅘ"]:
                    # 아 계열
                    if jung == "ㅘ":  # ㅗ+ㅏ→ㅘ 축약
                        stem_char = compose(cho, "ㅗ", " ")
                    else:
                        stem_char = base_char

                    stem = (
                        conjugated[:-1] + stem_char
                        if len(conjugated) > 1
                        else stem_char
                    )
                    results.append((stem, "았"))

                elif jung in ["ㅓ", "ㅜ", "ㅝ", "ㅣ", "ㅔ", "ㅐ"]:
                    # 어 계열
                    if jung == "ㅝ":  # ㅜ+ㅓ→ㅝ 축약
                        stem_char = compose(cho, "ㅜ", " ")
                    else:
                        stem_char = base_char

                    stem = (
                        conjugated[:-1] + stem_char
                        if len(conjugated) > 1
                        else stem_char
                    )
                    results.append((stem, "었"))

                # ㅡ 탈락: 써 → 쓰
                if jung in ["ㅓ", "ㅏ"]:
                    stem_eu = compose(cho, "ㅡ", " ")
                    if stem_eu:
                        ending = "었" if jung == "ㅓ" else "았"
                        stem = (
                            conjugated[:-1] + stem_eu
                            if len(conjugated) > 1
                            else stem_eu
                        )
                        results.append((stem, ending))

        # 2.2. 종성 없음 → 현재형 (아/어)
        elif jong == " ":
            if jung == "ㅘ":  # 와 → 오+아
                stem_char = compose(cho, "ㅗ", " ")
                stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
                results.append((stem, "아"))

            elif jung == "ㅝ":  # 워 → 우+어
                stem_char = compose(cho, "ㅜ", " ")
                stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
                results.append((stem, "어"))

            # ㅡ 탈락
            elif jung in ["ㅓ", "ㅏ"]:
                stem_eu = compose(cho, "ㅡ", " ")
                if stem_eu:
                    ending = "어" if jung == "ㅓ" else "아"
                    stem = conjugated[:-1] + stem_eu if len(conjugated) > 1 else stem_eu
                    results.append((stem, ending))

        return results if results else [(conjugated, "")]


if __name__ == "__main__":
    print("Conjugation 축약형 복원 테스트\n")

    analyzer = ConjugationAnalyzer()

    test_cases = [
        ("갔", "가 + 았"),
        ("왔", "오 + 았"),
        ("먹었", "먹 + 었"),
        ("좋았", "좋 + 았"),
        ("와", "오 + 아"),
        ("써", "쓰 + 어"),
    ]

    for surface, expected in test_cases:
        results = analyzer.restore_verb_stem(surface)
        if results:
            stem, ending = results[0]
            print(f"✓ {surface} → {stem} + {ending} (예상: {expected})")
        else:
            print(f"✗ {surface} → 실패 (예상: {expected})")
