
from typing import Tuple, Optional

# Unicode Constants
HANGUL_BASE = 0xAC00
HANGUL_END = 0xD7A3
CHO_BASE = 0x1100
JUNG_BASE = 0x1161
JONG_BASE = 0x11A7

# Hangul Lists
CHOSUNG = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


# ============================================================
# Functions
# ============================================================

def is_hangul(char: str) -> bool:
    """Check if a character is a Hangul syllable."""
    if not char:
        return False
    code = ord(char)
    return HANGUL_BASE <= code <= HANGUL_END

def decompose(ch: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """한글 자모 분해"""
    if not ch or len(ch) != 1:
        return (None, None, None)

    code = ord(ch) - HANGUL_BASE
    if code < 0 or code > HANGUL_END - HANGUL_BASE:
        return (None, None, None)

    jong = code % 28
    jung = ((code - jong) // 28) % 21
    cho = ((code - jong) // 28) // 21

    return (CHOSUNG[cho], JUNGSUNG[jung], JONGSUNG[jong])

def decompose_korean(text: str) -> list:
    """Decompose a string of Hangul syllables into (Cho, Jung, Jong) tuples."""
    results = []
    for char in text:
        results.append(decompose(char))
    return results

def compose(cho: str, jung: str, jong: str) -> Optional[str]:
    """한글 자모 결합"""
    if not cho or not jung:
        return None

    jong_idx = JONGSUNG.index(jong) if jong in JONGSUNG else 0
    code = HANGUL_BASE + CHOSUNG.index(cho) * 588 + JUNGSUNG.index(jung) * 28 + jong_idx
    return chr(code)

def compose_korean(text: list) -> str:
    """Compose a string of (Cho, Jung, Jong) tuples into a string of Hangul syllables."""
    results = []
    for cho, jung, jong in text:
        results.append(compose(cho, jung, jong))
    return ''.join(results)

def has_jongsung(char: str) -> bool:
    """Check if a Hangul syllable has a Jongsung (final consonant)."""
    if not is_hangul(char):
        return False
    return (ord(char) - HANGUL_BASE) % 28 != 0
