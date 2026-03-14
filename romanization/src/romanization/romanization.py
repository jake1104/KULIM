import hangul
from pronunciation.pronunciation import pronounce

# Revised Romanization Mappings
CHO_MAP = {
    "ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt",
    "ㄹ": "r", "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s",
    "ㅆ": "ss", "ㅇ": "", "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch",
    "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h"
}

JUNG_MAP = {
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae",
    "ㅓ": "eo", "ㅔ": "e", "ㅕ": "yeo", "ㅖ": "ye",
    "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe", "ㅛ": "yo",
    "ㅜ": "u", "ㅝ": "wo", "ㅞ": "we", "ㅟ": "wi", "ㅠ": "yu",
    "ㅡ": "eu", "ㅢ": "ui", "ㅣ": "i"
}

# Pronunciation-based Jongsung Mapping (Standard RR)
# maps pronunciation to romanization (e.g. 종성 ㄱ -> k)
JONG_MAP = {
    "": "",
    "ㄱ": "k", "ㄲ": "k", "ㄳ": "k",
    "ㄴ": "n", "ㄵ": "n", "ㄶ": "n",
    "ㄷ": "t",
    "ㄹ": "l", "ㄺ": "k", "ㄻ": "m", "ㄼ": "l", "ㄽ": "l", "ㄾ": "l", "ㄿ": "p", "ㅀ": "l",
    "ㅁ": "m",
    "ㅂ": "p", "ㅄ": "p",
    "ㅅ": "t", "ㅆ": "t",
    "ㅇ": "ng",
    "ㅈ": "t", "ㅊ": "t",
    "ㅋ": "k", "ㅌ": "t",
    "ㅍ": "p", "ㅎ": "t"
}

# Literal Transliteration Mapping
# maps spelling directly (e.g. 종성 ㄱ -> g, ㄹ -> l)
# Used for romanize_standard (User request: 읽고 -> ilggo) -> 읽(ilg) + 고(go)
JONG_MAP_LITERAL = {
    "": "",
    "ㄱ": "g", "ㄲ": "kk", "ㄳ": "gs", 
    "ㄴ": "n", "ㄵ": "nj", "ㄶ": "nh",
    "ㄷ": "d", "ㄹ": "l", 
    "ㄺ": "lg", "ㄻ": "lm", "ㄼ": "lb", "ㄽ": "ls", "ㄾ": "lt", "ㄿ": "lp", "ㅀ": "lh",
    "ㅁ": "m",
    "ㅂ": "b", "ㅄ": "bs",
    "ㅅ": "s", "ㅆ": "ss",
    "ㅇ": "ng",
    "ㅈ": "j", "ㅊ": "ch", 
    "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h"
}


def romanize_pronunciation(text: str, morph_analyzer=None) -> str:
    """
    Standard Revised Romanization based on pronunciation.
    Ex: 읽고 -> [일꼬] -> ilkko
    """
    # 1. Get standard pronunciation
    # 로마자 표기법 준수를 위해 is_romanization 플래그 전달
    p_text = pronounce(text, morph_analyzer=morph_analyzer, is_romanization=True)
    
    res = []
    for char in p_text:
        if hangul.is_hangul(char):
            cho, jung, jong = hangul.decompose(char)
            
            # Use RR maps
            # Note: Initial ㄱ,ㄷ,ㅂ in RR vary by position (voiceless/voiced).
            # But standard map usually simplifes or assumes context. 
            # Ideally RR distinguishes Initial G/K based on previous sound. 
            # For "ilkko", '일' ends in l, '꼬' starts with kk.
            
            r_cho = CHO_MAP.get(cho, "")
            r_jung = JUNG_MAP.get(jung, "")
            r_jong = JONG_MAP.get(jong, "")
            
            # 로마자 표기법 예외: 'ㄹㄹ'은 'll'로 적음 (예: 신라 -> [실라] -> silla)
            if r_cho == "r" and res and res[-1].endswith("l"):
                r_cho = "l"
            
            res.append(r_cho + r_jung + r_jong)
        else:
            res.append(char)
            
    return "".join(res)

def romanize_standard(text: str) -> str:
    """
    Literal Transliteration (Spelling-based).
    Ex: 읽고 -> ilggo
    """
    res = []
    for char in text:
        if hangul.is_hangul(char):
            cho, jung, jong = hangul.decompose(char)
            
            r_cho = CHO_MAP.get(cho, "")
            r_jung = JUNG_MAP.get(jung, "")
            r_jong = JONG_MAP_LITERAL.get(jong, "") # Use literal map for coda
            
            res.append(r_cho + r_jung + r_jong)
        else:
            res.append(char)
            
    return "".join(res)

def romanize(text: str, morph_analyzer=None) -> str:
    """Default alias to pronunciation-based romanization."""
    return romanize_pronunciation(text, morph_analyzer=morph_analyzer)

def romanize_korean(text: str, morph_analyzer=None) -> str:
    return romanize(text, morph_analyzer=morph_analyzer)
