from typing import Optional, Tuple
import re
from hangul import compose, decompose


class IrregularConjugation:
    """
    한국어 불규칙 활용 처리

    6가지 불규칙:
    1. ㅂ 불규칙: 돕다 → 도와, 도우니
    2. ㄷ 불규칙: 듣다 → 들어, 들으니
    3. ㅅ 불규칙: 짓다 → 지어, 지으니
    4. ㅎ 불규칙: 그렇다 → 그래, 그러니
    5. 르 불규칙: 부르다 → 불러, 부르니
    6. 으 불규칙: 쓰다 → 써, 쓰니
    """

    def __init__(self):
        # 불규칙 동사/형용사 목록
        # 키: 어간(받침 포함), 값: 기본형
        self.b_irregular = {
            "돕": "돕다",
            "곱": "곱다",
            "눕": "눕다",
            "줍": "줍다",
            "굽": "굽다",
            "가깝": "가깝다",  # 가까우 -> 가깝
            "고맙": "고맙다",  # 고마우 -> 고맙
            "즐겁": "즐겁다",  # 즐거우 -> 즐겁
            "아름답": "아름답다",  # 아름다우 -> 아름답
            "무겁": "무겁다",
            "차갑": "차갑다",
            "뜨겁": "뜨겁다",
            "반갑": "반갑다",
            "어렵": "어렵다",
            "쉽": "쉽다",
            "더럽": "더럽다",
            "무섭": "무섭다",
            "귀엽": "귀엽다",
            "부끄럽": "부끄럽다",
        }

        self.d_irregular = {
            "듣": "듣다",
            "걷": "걷다",
            "묻": "묻다",
            "싣": "싣다",
            "깨닫": "깨닫다",
        }

        self.s_irregular = {
            "짓": "짓다",
            "낫": "낫다",
            "잇": "잇다",
            "붓": "붓다",
        }

        self.h_irregular = {
            "그렇": "그렇다",
            "이렇": "이렇다",
            "저렇": "저렇다",
            "어떻": "어떻다",
            "하얗": "하얗다",
            "까맣": "까맣다",
            "빨갛": "빨갛다",
            "파랗": "파랗다",
            "노랗": "노랗다",
        }

        self.reu_irregular = {
            "부르": "부르다",
            "오르": "오르다",
            "다르": "다르다",
            "빠르": "빠르다",
            "이르": "이르다",
            "모르": "모르다",
            "흐르": "흐르다",
            "기르": "기르다",
        }

        self.eu_irregular = {
            "쓰": "쓰다",
            "끄": "끄다",
            "크": "크다",
            "뜨": "뜨다",
            "잠그": "잠그다",
            "기쁘": "기쁘다",  # b_irregular에서 이동
            "슬프": "슬프다",
            "바쁘": "바쁘다",
            "아프": "아프다",
        }

    def restore_b_irregular(self, surface: str) -> Optional[Tuple[str, str]]:
        """
        ㅂ 불규칙 복원

        Examples:
            도와 → 돕 + 아
            도우니 → 돕 + 니
        """
        # 와, 워 → ㅂ
        if surface.endswith("와"):
            base = surface[:-1]
            if base:
                last_char = base[-1]
                cho, jung, _ = decompose(last_char)
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last

                # print(f"DEBUG: b_irregular check '와': surface={surface}, stem={stem}, in_dict={stem in self.b_irregular}")
                if stem in self.b_irregular:
                    return (stem, "아")

        if surface.endswith("워"):
            base = surface[:-1]
            if base:
                last_char = base[-1]
                cho, jung, _ = decompose(last_char)
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last

                if stem in self.b_irregular:
                    return (stem, "어")

        # 우 → ㅂ
        if surface.endswith("우"):
            base = surface[:-1]
            if base:
                last_char = base[-1]
                cho, jung, _ = decompose(last_char)
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last

                if stem in self.b_irregular:
                    return (stem, "어")  # 단순화: '어'로 가정하거나 빈 문자열

        # 운 → ㅂ + 은
        if surface.endswith("운"):
            base = surface[:-1]
            if base:
                last_char = base[-1]
                cho, jung, _ = decompose(last_char)
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last

                # print(f"DEBUG: check '운': surface={surface}, stem={stem}, in_dict={stem in self.b_irregular}")
                if stem in self.b_irregular:
                    return (stem, "은")

        return None

    def restore_d_irregular(self, surface: str) -> Optional[Tuple[str, str]]:
        """
        ㄷ 불규칙 복원

        Examples:
            들어 → 듣 + 어
            들으니 → 듣 + 으니
        """
        # ㄷ -> ㄹ (모음 어미 앞)
        for stem, base in self.d_irregular.items():
            # stem: 듣 (ㄷ 받침)
            # changed: 들 (ㄹ 받침)
            cho, jung, jong = decompose(stem[-1])
            if jong != "ㄷ":
                continue

            changed_char = compose(cho, jung, "ㄹ")
            stem_prefix = stem[:-1] + changed_char

            if surface.startswith(stem_prefix):
                ending = surface[len(stem_prefix) :]
                # 어미는 모음으로 시작해야 함 (단순화: 일단 매칭되면 리턴)
                return (stem, ending)

        return None

    def restore_s_irregular(self, surface: str) -> Optional[Tuple[str, str]]:
        """
        ㅅ 불규칙 복원

        Examples:
            지어 → 짓 + 어
            지으니 → 짓 + 으니
        """
        # ㅅ이 탈락하고 이/으 추가
        for stem, base in self.s_irregular.items():
            # stem: 짓, 낫, 잇, 붓 (1글자)
            # stem_sound: 지, 나, 이, 부

            last_char = stem[-1]
            cho, jung, jong = decompose(last_char)

            # 종성이 'ㅅ'이어야 함
            if jong != "ㅅ":
                continue

            base_char = compose(cho, jung, " ")
            stem_sound = stem[:-1] + base_char

            if surface.startswith(stem_sound):
                ending = surface[len(stem_sound) :]
                return (stem, ending)

        return None

    def restore_h_irregular(self, surface: str) -> Optional[Tuple[str, str]]:
        """
        ㅎ 불규칙 복원

        Examples:
            그래 → 그렇 + 아 (ㅎ + 아 → ㅐ)
            그러니 → 그렇 + 니
        """
        for stem, base in self.h_irregular.items():
            stem_base = stem[:-1]  # ㅎ 제거

            # ㅎ + 아 → ㅐ
            if surface == stem_base + "래":
                return (stem, "아")

            # ㅎ 탈락
            if surface.startswith(stem_base + "러"):
                ending = surface[len(stem_base + "러") :]
                return (stem, "어" + ending)

        return None

    def restore_reu_irregular(self, surface: str) -> Optional[Tuple[str, str]]:
        """
        르 불규칙 복원

        Examples:
            불러 → 부르 + 어 (르 + 어 → 라/러)
            부르니 → 부르 + 니
        """
        # 부르 -> 불 + 러
        for stem, base in self.reu_irregular.items():
            # stem: 부르
            if not stem.endswith("르"):
                continue

            # prefix: 부
            prefix = stem[:-1]
            if not prefix:
                continue  # 1글자 '르'? (x)

            # modified prefix: 불 (attach ㄹ to prefix)
            p_last = prefix[-1]
            cho, jung, jong = decompose(p_last)
            if jong != " ":
                continue  # Already has batchim? (e.g. 구르?) Usually simple vowel.

            mod_prefix_char = compose(cho, jung, "ㄹ")
            mod_prefix = prefix[:-1] + mod_prefix_char

            # Check starts with '불'
            if surface.startswith(mod_prefix):
                # next char should be '러' or '라'
                rest = surface[len(mod_prefix) :]
                if not rest:
                    continue

                first_rest = rest[0]  # 러
                cho_r, jung_r, _ = decompose(first_rest)

                if cho_r == "ㄹ":
                    # found: 불 + 러 -> 부르 + 어
                    # recover ending: 러 -> 어 ?
                    # jung_r is ㅓ or ㅏ
                    if jung_r == "ㅓ":
                        ending = "어"
                    elif jung_r == "ㅏ":
                        ending = "아"
                    else:
                        ending = rest  # fallback

                    if len(rest) > 1:
                        ending += rest[1:]

                    return (stem, ending)

        return None

    def restore_eu_irregular(self, surface: str) -> Optional[Tuple[str, str]]:
        """
        으 불규칙 복원

        Examples:
            써 → 쓰 + 어 (ㅡ 탈락)
            쓰니 → 쓰 + 니
        """
        for stem, base in self.eu_irregular.items():
            # 모음으로 시작하는 어미 앞에서 ㅡ 탈락
            stem_prefix = stem[:-1]

            if not stem_prefix:  # 1글자 어간 (쓰, 끄, 크...)
                # 초성이 같은지 확인
                if not surface:
                    continue
                cho_stem, _, _ = decompose(stem[0])
                cho_surf, _, _ = decompose(surface[0])
                if cho_stem != cho_surf:
                    continue

                # 어미 분리 시도 (단순화: 모음이 'ㅓ'나 'ㅏ'인 경우)
                _, jung_surf, _ = decompose(surface[0])
                if jung_surf in ["ㅓ", "ㅏ", "ㅕ", "ㅑ"]:
                    # 써 -> 쓰 + 어
                    if jung_surf == "ㅓ":
                        ending = "어"
                    elif jung_surf == "ㅏ":
                        ending = "아"
                    else:
                        ending = surface[0]  # Fallback

                    if len(surface) > 1:
                        ending += surface[1:]

                    return (stem, ending)

            elif surface.startswith(stem_prefix):  # 2글자 이상 (아프, 슬프...)
                # ㅡ 없는 부분 (앞)
                ending = surface[len(stem_prefix) :]
                if ending and ending[0] in "ㅓㅏㅕㅑ어아여야":
                    return (stem, ending)

        return None

    def restore_any(self, surface: str) -> Optional[Tuple[str, str, str]]:
        """
        모든 불규칙 활용 시도

        Returns:
            (어간, 어미, 불규칙타입) or None
        """
        # ㅂ 불규칙
        result = self.restore_b_irregular(surface)
        if result:
            return (*result, "ㅂ")

        # ㄷ 불규칙
        result = self.restore_d_irregular(surface)
        if result:
            return (*result, "ㄷ")

        # ㅅ 불규칙
        result = self.restore_s_irregular(surface)
        if result:
            return (*result, "ㅅ")

        # ㅎ 불규칙
        result = self.restore_h_irregular(surface)
        if result:
            return (*result, "ㅎ")

        # 르 불규칙
        result = self.restore_reu_irregular(surface)
        if result:
            return (*result, "르")

        # 으 불규칙
        result = self.restore_eu_irregular(surface)
        if result:
            return (*result, "으")

        return None


if __name__ == "__main__":
    # 테스트
    irregular = IrregularConjugation()

    test_cases = [
        ("도와", "돕/ㅂ + 아"),
        ("들어", "듣/ㄷ + 어"),
        ("지어", "짓/ㅅ + 어"),
        ("그래", "그렇/ㅎ + 아"),
        ("불러", "부르/르 + 어"),
        ("써", "쓰/으 + 어"),
        ("아름다운", "아름답/ㅂ + 은"),
    ]

    print("불규칙 활용 테스트:\n")
    for surface, expected in test_cases:
        result = irregular.restore_any(surface)
        if result:
            stem, ending, irr_type = result
            print(f"✓ {surface} → {stem}/{irr_type} + {ending} (예상: {expected})")
        else:
            print(f"✗ {surface} → 실패 (예상: {expected})")
