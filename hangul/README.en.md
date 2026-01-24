# KULIM Hangul

<p align="center">
  <img src="https://img.shields.io/badge/package-hangul-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.1.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-korean-green.svg?style=flat-square" alt="Korean"></a>
</p>

---

## Overview

**KULIM Hangul** is a lightweight pure-Python utility package for Hangul (Korean alphabet) processing.
It provides core functionality for Hangul preprocessing, including character decomposition, composition, and validation, with zero external dependencies.

### Key Features

- **Zero Dependency**: Instantly integrable without any external library dependencies
- **Old Hangul Support**: Full support for Old Hangul and extended Jamo ranges
- **High Performance**: Optimized Unicode-based bit operations for fast bulk text processing
- **Linguistic Precision**: Perfect support for linguistic distinctions between initial consonants (Chosung), medial vowels (Jungsung), and final consonants (Jongsung)

---

## Installation

```bash
# Install as standalone package
pip install hangul

# Included in KULIM integrated package
pip install kulim
```

---

## Usage

### 1. Character Decomposition and Composition

```python
from hangul import decompose, compose, decompose_korean

# Decompose single character: '한' -> ('ㅎ', 'ㅏ', 'ㄴ')
cho, jung, jong = decompose("한")
print(f"Cho: {cho}, Jung: {jung}, Jong: {jong}")
# Output: Cho: ㅎ, Jung: ㅏ, Jong: ㄴ

# Decompose entire string
result = decompose_korean("한글")
print(result)
# Output: [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]

# Compose Jamo: ('ㅎ', 'ㅏ', 'ㄴ') -> '한'
char = compose("ㅎ", "ㅏ", "ㄴ")
print(char)  # Output: 한

# Handle complex final consonants
cho, jung, jong = decompose("값")
print(f"{cho}, {jung}, {jong}")  # Output: ㄱ, ㅏ, ㅄ
```

### 2. Hangul Utilities

```python
from hangul import is_hangul, has_jongsung

# Check if character is Hangul (modern + old Hangul)
print(is_hangul("가"))   # True
print(is_hangul("A"))    # False
print(is_hangul("\u1100"))  # True (Old Hangul Chosung ᄀ)

# Check for final consonant (Jongsung)
print(has_jongsung("국"))  # True
print(has_jongsung("가"))  # False
print(has_jongsung("값"))  # True (complex Jongsung ㅄ)
```

### 3. Old Hangul Support

Extended Jamo ranges are supported from v0.1.0.

```python
from hangul import is_hangul, decompose

# Recognize Old Hangul Jamo
old_cho = "\u1100"  # ᄀ (Hangul Jamo)
old_jung = "\uA960"  # ꥠ (Hangul Jamo Extended-A)
old_jong = "\uD7B0"  # ힰ (Hangul Jamo Extended-B)

print(is_hangul(old_cho))   # True
print(is_hangul(old_jung))  # True
print(is_hangul(old_jong))  # True

# Decompose Old Hangul Jamo (non-precomposed)
cho, jung, jong = decompose(old_cho)
print(cho)  # ᄀ (returned in Chosung position)
```

**Supported Unicode Ranges:**

- Hangul Syllables: `0xAC00-0xD7A3` (Modern Hangul)
- Hangul Jamo: `0x1100-0x11FF` (Old Hangul Jamo)
- Hangul Jamo Extended-A: `0xA960-0xA97F`
- Hangul Jamo Extended-B: `0xD7B0-0xD7FF`

---

## API Reference

### Core Functions

| Function                      | Description                                         | Return Type                  |
| :---------------------------- | :-------------------------------------------------- | :--------------------------- |
| `decompose(char)`             | Decompose Hangul syllable into Cho, Jung, Jong      | `tuple[str, str, str]`       |
| `compose(cho, jung, jong="")` | Compose Jamo into Hangul syllable                   | `str`                        |
| `decompose_korean(text)`      | Decompose entire string into Jamo units             | `list[tuple[str, str, str]]` |
| `compose_korean(jamos)`       | Compose Jamo list into Hangul string                | `str`                        |
| `is_hangul(char)`             | Check if character is Hangul (including Old Hangul) | `bool`                       |
| `has_jongsung(char)`          | Check if character has final consonant              | `bool`                       |

### Constants

```python
from hangul import CHOSUNG, JUNGSUNG, JONGSUNG

# Chosung list (19 consonants)
print(len(CHOSUNG))  # 19
print(CHOSUNG[0])    # 'ㄱ'

# Jungsung list (21 vowels)
print(len(JUNGSUNG))  # 21
print(JUNGSUNG[0])    # 'ㅏ'

# Jongsung list (28 final consonants, including empty)
print(len(JONGSUNG))  # 28
print(JONGSUNG[0])    # '' (empty Jongsung)
print(JONGSUNG[1])    # 'ㄱ'
```

---

## Advanced Usage

### Chosung Search

```python
from hangul import decompose

def get_chosung(text):
    """Extract only initial consonants from text"""
    result = []
    for char in text:
        if ord('가') <= ord(char) <= ord('힣'):
            cho, _, _ = decompose(char)
            result.append(cho)
        else:
            result.append(char)
    return ''.join(result)

# Chosung search indexing
print(get_chosung("안녕하세요"))  # ㅇㄴㅎㅅㅇ
print(get_chosung("대한민국"))    # ㄷㅎㅁㄱ
```

### Jamo Normalization

```python
from hangul import decompose, compose

def normalize_jamo(text):
    """Normalize complex Jamo to single Jamo"""
    result = []
    for char in text:
        if ord('가') <= ord(char) <= ord('힣'):
            cho, jung, jong = decompose(char)
            # Handle complex final consonants: ㄳ -> ㄱ
            if jong in ['ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ']:
                jong = jong[0]  # Use only first consonant
            result.append(compose(cho, jung, jong))
        else:
            result.append(char)
    return ''.join(result)

print(normalize_jamo("값"))  # 갑
print(normalize_jamo("닭"))  # 닥
```

---

## Performance

### Bulk Text Processing

```python
from hangul import decompose_korean
import time

# Benchmark: 100,000 characters
text = "한글" * 50000
start = time.time()
result = decompose_korean(text)
elapsed = time.time() - start

print(f"Processing time: {elapsed:.3f}s")
print(f"Speed: {len(text)/elapsed:.0f} chars/sec")
# Typically 100,000+ chars/sec performance
```

---

## Troubleshooting

### FAQ

**Q: Old Hangul Jamo are not displaying correctly.**
A: Check if your terminal font supports Old Hangul Unicode ranges. We recommend `Noto Sans CJK` or `NanumGothicCoding` fonts.

**Q: `compose()` function returns an empty string.**
A: Verify that the input Jamo form a valid combination. For example, `compose("ㅏ", "ㅏ", "")` is invalid.

**Q: Can complex final consonants (e.g., ㄳ, ㄺ) be separated into individual consonants?**
A: The current version returns complex final consonants as single strings. Use a separate mapping table if individual separation is needed.

---

## License

This module is distributed under the [MIT License](../../LICENSE).
For contributions and bug reports, please use [GitHub Issues](https://github.com/jake1104/KULIM/issues).

---

<p align="center">
  Part of the KULIM Framework
</p>
