from typing import Optional, Tuple
from hangul import compose, decompose


class IrregularConjugation:
    def __init__(self):
        self.b_irregular = {
            "돕": "돕다", "곱": "곱다", "눕": "눕다", "줍": "줍다", "굽": "굽다",
            "가깝": "가깝다", "고맙": "고맙다", "즐겁": "즐겁다",
            "아름답": "아름답다", "무겁": "무겁다", "차갑": "차갑다",
            "뜨겁": "뜨겁다", "반갑": "반갑다", "어렵": "어렵다",
            "쉽": "쉽다", "더럽": "더럽다", "무섭": "무섭다",
            "귀엽": "귀엽다", "부끄럽": "부끄럽다", "가볍": "가볍다",
            "맵": "맵다", "밝": "밝다", "어둡": "어둡다",
        }

        self.d_irregular = {
            "듣": "듣다", "걷": "걷다", "묻": "묻다", "싣": "싣다",
            "깨닫": "깨닫다", "눋": "눋다",
        }

        self.s_irregular = {
            "짓": "짓다", "낫": "낫다", "잇": "잇다", "붓": "붓다",
            "긋": "긋다",
        }

        self.h_irregular = {
            "그렇": "그렇다", "이렇": "이렇다", "저렇": "저렇다",
            "어떻": "어떻다",
            "하얗": "하얗다", "까맣": "까맣다", "빨갛": "빨갛다",
            "파랗": "파랗다", "노랗": "노랗다", "새하얗": "새하얗다",
            "시커맣": "시커맣다", "새빨갛": "새빨갛다", "시뻘겋": "시뻘겋다",
            "새파랗": "새파랗다", "시퍼렇": "시퍼렇다", "누렇": "누렇다",
            "허옇": "허옇다", "퍼렇": "퍼렇다",
        }

        self.reu_irregular = {
            "부르": "부르다", "오르": "오르다", "다르": "다르다",
            "빠르": "빠르다", "이르": "이르다", "모르": "모르다",
            "흐르": "흐르다", "기르": "기르다", "나르": "나르다",
            "자르": "자르다", "가르": "가르다", "고르": "고르다",
            "마르": "마르다", "서투르": "서투르다", "두르": "두르다",
            "누르": "누르다",
        }

        self.eu_irregular = {
            "쓰": "쓰다", "끄": "끄다", "크": "크다", "뜨": "뜨다",
            "잠그": "잠그다", "기쁘": "기쁘다", "슬프": "슬프다",
            "바쁘": "바쁘다", "아프": "아프다", "고프": "고프다",
            "배고프": "배고프다", "배부르": "배부르다",
            "예쁘": "예쁘다", "나쁘": "나쁘다",
            "크": "크다", "다르": "다르다",
        }

        self.yeo_irregular = {
            "하": "하다",
        }

    def restore_any(self, surface):
        for name, method in [
            ("여", self._restore_yeo),
            ("ㅎ", self._restore_h),
            ("ㅂ", self._restore_b),
            ("르", self._restore_reu),
            ("ㄷ", self._restore_d),
            ("ㅅ", self._restore_s),
            ("으", self._restore_eu),
        ]:
            result = method(surface)
            if result:
                return (*result, name)
        return None

    def _restore_yeo(self, surface) -> Optional[Tuple[str, str]]:
        if surface == "해":
            return ("하", "여")
        if surface.startswith("해"):
            return ("하", "여" + surface[1:])
        if surface == "하여":
            return ("하", "여")
        if surface == "했":
            return ("하", "였")
        if surface.endswith("했"):
            base = surface[:-1]
            return ("하", "였")
        if surface.startswith("하"):
            ending = surface[1:]
            if ending in ["고", "지", "게", "면", "니", "나", "네", "다", "며",
                           "지만", "니까", "는데", "도록", "려고", "아", "어",
                           "아서", "어서", "지만"]:
                return ("하", ending)
        return None

    def _restore_h(self, surface) -> Optional[Tuple[str, str]]:
        for stem in self.h_irregular:
            if surface == stem[:-1] + "래":
                return (stem, "아")
            if surface == stem[:-1] + "래요":
                return (stem, "아요")
            if surface.startswith(stem[:-1] + "래"):
                return (stem, "아" + surface[len(stem[:-1] + "래"):])

        for stem in self.h_irregular:
            if surface.startswith(stem[:-1] + "러"):
                ending = surface[len(stem[:-1] + "러"):]
                return (stem, "어" + ending)

        for stem in self.h_irregular:
            if surface.startswith(stem[:-1]):
                rest = surface[len(stem[:-1]):]
                if rest and rest[0] not in ["아", "어", "여", "에", "애"]:
                    return (stem, rest)

        return None

    def _restore_b(self, surface) -> Optional[Tuple[str, str]]:
        if surface.endswith("와"):
            base = surface[:-1]
            if base:
                cho, jung, _ = decompose(base[-1])
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last
                if stem in self.b_irregular:
                    return (stem, "아")
        if surface.endswith("워"):
            base = surface[:-1]
            if base:
                cho, jung, _ = decompose(base[-1])
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last
                if stem in self.b_irregular:
                    return (stem, "어")
        if surface.endswith("우"):
            base = surface[:-1]
            if base:
                cho, jung, _ = decompose(base[-1])
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last
                if stem in self.b_irregular:
                    return (stem, "어")
        if surface.endswith("운"):
            base = surface[:-1]
            if base:
                cho, jung, _ = decompose(base[-1])
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last
                if stem in self.b_irregular:
                    return (stem, "은")
        if surface.endswith("울"):
            base = surface[:-1]
            if base:
                cho, jung, _ = decompose(base[-1])
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last
                if stem in self.b_irregular:
                    return (stem, "ㄹ")
        if surface.endswith("우니"):
            base = surface[:-2]
            if base:
                cho, jung, _ = decompose(base[-1])
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last
                if stem in self.b_irregular:
                    return (stem, "니")
        if surface.endswith("워서"):
            base = surface[:-2]
            if base:
                cho, jung, _ = decompose(base[-1])
                stem_last = compose(cho, jung, "ㅂ")
                stem = base[:-1] + stem_last
                if stem in self.b_irregular:
                    return (stem, "어서")
        return None

    def _restore_d(self, surface) -> Optional[Tuple[str, str]]:
        for stem in self.d_irregular:
            cho, jung, jong = decompose(stem[-1])
            if jong != "ㄷ":
                continue
            changed_char = compose(cho, jung, "ㄹ")
            stem_prefix = stem[:-1] + changed_char
            if surface.startswith(stem_prefix):
                ending = surface[len(stem_prefix):]
                return (stem, ending)
        return None

    def _restore_s(self, surface) -> Optional[Tuple[str, str]]:
        for stem in self.s_irregular:
            last_char = stem[-1]
            cho, jung, jong = decompose(last_char)
            if jong != "ㅅ":
                continue
            base_char = compose(cho, jung, "")
            stem_sound = stem[:-1] + base_char
            if surface.startswith(stem_sound):
                ending = surface[len(stem_sound):]
                return (stem, ending)
        return None

    def _restore_reu(self, surface) -> Optional[Tuple[str, str]]:
        for stem in self.reu_irregular:
            if not stem.endswith("르"):
                continue
            prefix = stem[:-1]
            if not prefix:
                continue
            p_last = prefix[-1]
            cho, jung, jong = decompose(p_last)
            if jong != "":
                continue
            mod_prefix_char = compose(cho, jung, "ㄹ")
            mod_prefix = prefix[:-1] + mod_prefix_char
            if surface.startswith(mod_prefix):
                rest = surface[len(mod_prefix):]
                if not rest:
                    continue
                first_rest = rest[0]
                cho_r, jung_r, _ = decompose(first_rest)
                if cho_r == "ㄹ":
                    if jung_r in ["ㅓ", "ㅕ"]:
                        ending = "어"
                    elif jung_r in ["ㅏ", "ㅑ"]:
                        ending = "아"
                    else:
                        ending = rest
                    if len(rest) > 1:
                        ending += rest[1:]
                    return (stem, ending)
        return None

    def _restore_eu(self, surface) -> Optional[Tuple[str, str]]:
        for stem in self.eu_irregular:
            stem_prefix = stem[:-1]
            if not stem_prefix:
                if not surface:
                    continue
                cho_stem, _, _ = decompose(stem[0])
                cho_surf, jung_surf, _ = decompose(surface[0])
                if cho_stem != cho_surf:
                    continue
                if jung_surf in ["ㅓ", "ㅏ", "ㅕ", "ㅑ"]:
                    if jung_surf in ["ㅓ", "ㅕ"]:
                        ending = "어"
                    else:
                        ending = "아"
                    if len(surface) > 1:
                        ending += surface[1:]
                    return (stem, ending)
            elif surface.startswith(stem_prefix):
                ending = surface[len(stem_prefix):]
                if ending and ending[0] in "어아여야":
                    return (stem, ending)
        return None



