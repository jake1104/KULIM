from typing import Tuple, Optional

# Unicode Constants (Modern)
HANGUL_BASE = 0xAC00
HANGUL_END = 0xD7A3

# Old Hangul / Jamo Ranges
# Hangul Jamo (0x1100-0x11FF): Modern & Old Jamos
JAMO_BASE = 0x1100
JAMO_END = 0x11FF

# Hangul Jamo Extended-A (0xA960-0xA97F): Old Choseongs
HJE_A_BASE = 0xA960
HJE_A_END = 0xA97F

# Hangul Jamo Extended-B (0xD7B0-0xD7FF): Old Jongseongs & Jungseongs
HJE_B_BASE = 0xD7B0
HJE_B_END = 0xD7FF

# Hangul Compatibility Jamo (0x3130-0x318F) - Modern isolated jamos
COMPAT_BASE = 0x3130
COMPAT_END = 0x318F


# Hangul Lists (Modern)
CHOSUNG = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


# ============================================================
# Functions
# ============================================================

def is_hangul(char: str) -> bool:
    """
    Check if a character is a Hangul syllable or Jamo (including Old Hangul).
    
    Includes:
    - Hangul Syllables (0xAC00 - 0xD7A3)
    - Hangul Jamo (0x1100 - 0x11FF)
    - Hangul Jamo Extended-A (0xA960 - 0xA97F)
    - Hangul Jamo Extended-B (0xD7B0 - 0xD7FF)
    - Hangul Compatibility Jamo (0x3130 - 0x318F)
    """
    if not char:
        return False
    code = ord(char)
    return (
        (HANGUL_BASE <= code <= HANGUL_END) or
        (JAMO_BASE <= code <= JAMO_END) or
        (HJE_A_BASE <= code <= HJE_A_END) or
        (HJE_B_BASE <= code <= HJE_B_END) or
        (COMPAT_BASE <= code <= COMPAT_END)
    )

def is_complete_hangul(char: str) -> bool:
    """Check if character is a precomposed modern Hangul syllable."""
    if not char: return False
    return HANGUL_BASE <= ord(char) <= HANGUL_END

def decompose(ch: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    한글 자모 분해.
    
    - Modern Syllable: Returns (Cho, Jung, Jong)
    - Old Hangul / Jamo: Returns (None, None, None) or specialized logic?
      Currently standard logic: if it's already decomposed (Jamo), we can't 'decompose' it further 
      into standard Cho/Jung/Jong slots in the same way because Old Hangul spans multiple chars.
      
      This function is primarily for Modern Syllable decomposition.
      For Old Hangul handling, usage of unicodedata.normalize('NFD', text) is recommended externally.
      
      If input is a single Jamo/Old Hangul char, it returns (ch, None, None) semantically? 
      Or just (None, None, None) to indicate it's not a composable syllable?
      
      Let's keep strict behavior: If it is a modern syllable, decompose.
      If it is a Jamo (Modern/Old), treat it as an atomic unit? 
      Actually, for consistency with 'pronunciation' module which expects list(decompose(char)),
      if it's not a precomposed syllable, it returns (None, None, None) now.
      
      Updated behavior: If it's a Jamo/Old Hangul char, return it as the 'Cho' component? 
      No, that breaks structure.
      
      Return (None, None, None) if not precomposed syllable (AC00-D7A3).
      But we can return the char itself if it's passed?
      
      Let's maintain backward compatibility: Only decompose AC00-D7A3.
    """
    if not ch or len(ch) != 1:
        return (None, None, None)

    code = ord(ch) - HANGUL_BASE
    
    # 1. Modern Precomposed Syllable
    if 0 <= code <= HANGUL_END - HANGUL_BASE:
        jong = code % 28
        jung = ((code - jong) // 28) % 21
        cho = ((code - jong) // 28) // 21
        return (CHOSUNG[cho], JUNGSUNG[jung], JONGSUNG[jong])

    # 2. Old Hangul / Jamo Handling (Not precomposed)
    # Check if it's a known Choseong, Jungsung, or Jongsung
    # Modern Jamo (11xx)
    # Extended A (A960) -> Cho
    # Extended B (D7B0) -> Jung (D7B0-D7C6), Jong (D7CB-D7FB)
    
    code_raw = ord(ch)
    
    # Choseong Range
    # 1100-115F (Modern/Old Cho), A960-A97F (Ext-A Cho)
    if (0x1100 <= code_raw <= 0x115F) or (0xA960 <= code_raw <= 0xA97F):
        return (ch, "", "")
        
    # Jungsung Range
    # 1160-11A2 (Modern/Old Jung), D7B0-D7C6 (Ext-B Jung)
    if (0x1160 <= code_raw <= 0x11A2) or (0xD7B0 <= code_raw <= 0xD7C6):
        return ("", ch, "")
        
    # Jongsung Range
    # 11A8-11F9 (Modern/Old Jong), D7CB-D7FB (Ext-B Jong)
    if (0x11A8 <= code_raw <= 0x11F9) or (0xD7CB <= code_raw <= 0xD7FB):
        return ("", "", ch)
        
    # Compat Jamo (3130-318F) - ambiguous, usually treated as Cho if consonant
    # For now, return (None, None, None) or handle specifically?
    # Consonants 3131-314E, Vowels 314F-3163
    if 0x3131 <= code_raw <= 0x314E or 0x3165 <= code_raw <= 0x318E: # Consonants
        return (ch, "", "") # As Cho
    if 0x314F <= code_raw <= 0x3163: # Vowels
        return ("", ch, "") # As Jung

    return (None, None, None)

def decompose_korean(text: str) -> list:
    """Decompose a string of Hangul syllables into (Cho, Jung, Jong) tuples."""
    results = []
    for char in text:
        results.append(decompose(char))
    return results

def compose(cho: str, jung: str, jong: str) -> Optional[str]:
    """한글 자모 결합 (Modern Syllables only)"""
    if not cho or not jung:
        return None

    try:
        jong_idx = JONGSUNG.index(jong) if jong in JONGSUNG else 0
        cho_idx = CHOSUNG.index(cho)
        jung_idx = JUNGSUNG.index(jung)
        
        code = HANGUL_BASE + cho_idx * 588 + jung_idx * 28 + jong_idx
        return chr(code)
    except ValueError:
        # If components are Old Hangul or invalid, fallback?
        # Standard compose logic only works for Modern.
        # For Old Hangul, one should just join the strings.
        return None

def compose_korean(text: list) -> str:
    """Compose a string of (Cho, Jung, Jong) tuples into a string of Hangul syllables."""
    results = []
    for cho, jung, jong in text:
        res = compose(cho, jung, jong)
        if res:
            results.append(res)
        else:
            # Fallback for non-composable parts
            if cho: results.append(cho)
            if jung: results.append(jung)
            if jong: results.append(jong)
    return ''.join(results)

def has_jongsung(char: str) -> bool:
    """Check if a Hangul syllable has a Jongsung (final consonant)."""
    if not is_complete_hangul(char):
        return False
    return (ord(char) - HANGUL_BASE) % 28 != 0
