from typing import List, Tuple, Optional
from hangul import compose, decompose

from .irregular import IrregularConjugation


class ConjugationAnalyzer:
    CONJUGATION_ENDINGS = [
        "아", "어", "았", "었", "고", "지", "게", "면", "서",
        "니", "나", "네", "다", "요", "도", "며", "면서",
        "지만", "니까", "아서", "어서", "러", "려고", "자",
        "는", "은", "을", "ㄴ", "ㄹ", "던", "기", "ㅁ",
        "습니다", "ㅂ니다", "구나", "군요", "네요", "어요",
        "아요", "는데", "은데", "ㄴ데", "거든", "든지",
        "도록", "을수록", "ㄹ수록", "으나", "아도", "어도",
        "았던", "었던",
    ]

    def __init__(self, trie=None):
        self.trie = trie
        self.irregular = IrregularConjugation()

    def restore_verb_stem(self, conjugated: str) -> List[Tuple[str, str]]:
        if not conjugated:
            return []

        results = []

        irr_result = self.irregular.restore_any(conjugated)
        if irr_result:
            stem, ending, irr_type = irr_result
            results.append((stem, ending))

        last_char = conjugated[-1]
        try:
            cho, jung, jong = decompose(last_char)
        except Exception:
            return results if results else [(conjugated, "")]

        if cho is None:
            return results if results else [(conjugated, "")]

        if jong == "ㅆ" or len(conjugated) >= 2 and conjugated[-2] == "았" or conjugated.endswith("었"):
            self._restore_past(conjugated, cho, jung, jong, results)
        elif jong == "":
            self._restore_present(conjugated, cho, jung, results)
        elif jong:
            self._restore_consonant(conjugated, cho, jung, jong, results)

        return self._deduplicate(results) if results else [(conjugated, "")]

    def _restore_past(self, conjugated, cho, jung, jong, results):
        if jong == "ㅆ":
            base_char = compose(cho, jung, "")
            if base_char:
                if jung in ["ㅏ", "ㅗ", "ㅘ"]:
                    stem_char = compose(cho, "ㅗ" if jung == "ㅘ" else cho if jung else "", "")
                    if jung == "ㅘ":
                        stem_char = compose(cho, "ㅗ", "")
                    else:
                        stem_char = base_char
                    stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
                    results.append((stem, "았"))
                elif jung in ["ㅓ", "ㅜ", "ㅝ", "ㅣ", "ㅔ", "ㅐ", "ㅕ", "ㅖ"]:
                    stem_char = compose(cho, "ㅜ" if jung == "ㅝ" else cho if jung else "", "")
                    if jung == "ㅝ":
                        stem_char = compose(cho, "ㅜ", "")
                    else:
                        stem_char = base_char
                    stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
                    results.append((stem, "었"))

                if jung in ["ㅓ", "ㅏ"]:
                    stem_eu = compose(cho, "ㅡ", "")
                    if stem_eu:
                        ending = "었" if jung == "ㅓ" else "았"
                        stem = conjugated[:-1] + stem_eu if len(conjugated) > 1 else stem_eu
                        results.append((stem, ending))

    def _restore_present(self, conjugated, cho, jung, results):
        if jung == "ㅘ":
            stem_char = compose(cho, "ㅗ", "")
            stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
            results.append((stem, "아"))
        elif jung == "ㅝ":
            stem_char = compose(cho, "ㅜ", "")
            stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
            results.append((stem, "어"))
        elif jung in ["ㅐ", "ㅔ"] and len(conjugated) >= 1:
            if jung == "ㅐ":
                pass
            elif jung == "ㅔ":
                pass
        elif jung in ["ㅓ", "ㅏ"]:
            stem_eu = compose(cho, "ㅡ", "")
            if stem_eu:
                ending = "어" if jung == "ㅓ" else "아"
                stem = conjugated[:-1] + stem_eu if len(conjugated) > 1 else stem_eu
                results.append((stem, ending))
        elif jung == "ㅕ":
            stem_char = compose(cho, "ㅣ", "")
            if stem_char:
                stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
                results.append((stem, "어"))
        elif jung == "ㅑ":
            stem_char = compose(cho, "ㅣ", "")
            if stem_char:
                stem = conjugated[:-1] + stem_char if len(conjugated) > 1 else stem_char
                results.append((stem, "아"))

    def _restore_consonant(self, conjugated, cho, jung, jong, results):
        base_no_jong = compose(cho, jung, "")
        if base_no_jong:
            if jung in ["ㅏ", "ㅑ", "ㅗ", "ㅘ"]:
                if len(conjugated) > 1:
                    stem_parts = list(conjugated[:-1] + base_no_jong)
                    stem_prefix = "".join(stem_parts[:-1]) if len(stem_parts) > 1 else ""
                    stem = stem_prefix + base_no_jong
                else:
                    stem = base_no_jong
                results.append((stem, "아"))
            else:
                if len(conjugated) > 1:
                    stem_parts = list(conjugated[:-1] + base_no_jong)
                    stem_prefix = "".join(stem_parts[:-1]) if len(stem_parts) > 1 else ""
                    stem = stem_prefix + base_no_jong
                else:
                    stem = base_no_jong
                results.append((stem, "어"))

    def _deduplicate(self, items):
        seen = set()
        result = []
        for stem, ending in items:
            if (stem, ending) not in seen:
                seen.add((stem, ending))
                result.append((stem, ending))
        return result



