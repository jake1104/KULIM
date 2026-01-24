# KULIM Romanization

<p align="center">
  <img src="https://img.shields.io/badge/package-romanization-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.1.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-korean-green.svg?style=flat-square" alt="Korean"></a>
</p>

---

## Overview

**KULIM Romanization** is a module for converting Hangul to Roman letters, based on the National Institute of Korean Language's **Revised Romanization of Korean**.
It provides two modes—phonetic-based and spelling-based romanization—to support various use cases.

### Key Features

- **Dual Modes**: Phonetic-based and Literal (spelling-based) conversion modes
- **Standard Compliance**: Adherence to National Institute of Korean Language romanization rules
- **Pronunciation Integration**: Integration with `pronunciation` module for accurate phonetic-based romanization
- **Flexible Mapping**: Support for custom mapping tables

---

## Installation

```bash
# Install as standalone package
pip install romanization

# Included in KULIM integrated package
pip install kulim
```

**Dependencies:**

- `hangul`: Jamo decomposition/composition functionality
- `pronunciation`: Pronunciation conversion functionality (used in phonetic mode)

---

## Usage

### 1. Phonetic-based Romanization (Phonetic Mode)

Converts to Roman letters based on standard pronunciation.

```python
from romanization import romanize, romanize_pronunciation

# Basic usage (romanize is an alias for romanize_pronunciation)
print(romanize("한글"))           # hangeul
print(romanize("대한민국"))       # daehanminguk

# Reflects pronunciation changes
print(romanize("밥이"))           # babi (Liaison)
print(romanize("국민"))           # gungmin (Nasalization)
print(romanize("같이"))           # gachi (Palatalization)
print(romanize("읽고"))           # ilkko (Tensification)
print(romanize("놓고"))           # noko (Aspiration)

# Explicit function usage
print(romanize_pronunciation("한국어"))  # hangugeo
```

### 2. Spelling-based Romanization (Literal Mode)

Converts spelling directly to Roman letters without pronunciation changes.

```python
from romanization import romanize_standard

# Spelling-based conversion
print(romanize_standard("한글"))     # hangeul
print(romanize_standard("읽고"))     # ilggo (pronunciation: ilkko)
print(romanize_standard("값이"))     # gabsi (pronunciation: gapssi)
print(romanize_standard("앉다"))     # anjda (pronunciation: antta)
print(romanize_standard("독립"))     # dogrib (pronunciation: dongnip)

# Complex final consonant handling
print(romanize_standard("닭"))       # dalg
print(romanize_standard("삶"))       # salm
```

### 3. Mode Comparison

```python
from romanization import romanize, romanize_standard

words = ["읽고", "값이", "앉다", "국민", "같이"]

print("Word\tPhonetic\tLiteral")
print("-" * 40)
for word in words:
    phonetic = romanize(word)
    literal = romanize_standard(word)
    print(f"{word}\t{phonetic}\t\t{literal}")

# Output:
# Word    Phonetic      Literal
# ----------------------------------------
# 읽고    ilkko          ilggo
# 값이    gapssi         gabsi
# 앉다    antta          anjda
# 국민    gungmin        gugmin
# 같이    gachi          gat-i
```

---

## Romanization Rules

### Consonant Romanization

#### Initial Consonants

| Hangul | Roman  | Example  |
| :----- | :----- | :------- |
| ㄱ     | g      | 가 → ga  |
| ㄲ     | kk     | 까 → kka |
| ㄴ     | n      | 나 → na  |
| ㄷ     | d      | 다 → da  |
| ㄸ     | tt     | 따 → tta |
| ㄹ     | r/l    | 라 → ra  |
| ㅁ     | m      | 마 → ma  |
| ㅂ     | b      | 바 → ba  |
| ㅃ     | pp     | 빠 → ppa |
| ㅅ     | s      | 사 → sa  |
| ㅆ     | ss     | 싸 → ssa |
| ㅇ     | (none) | 아 → a   |
| ㅈ     | j      | 자 → ja  |
| ㅉ     | jj     | 짜 → jja |
| ㅊ     | ch     | 차 → cha |
| ㅋ     | k      | 카 → ka  |
| ㅌ     | t      | 타 → ta  |
| ㅍ     | p      | 파 → pa  |
| ㅎ     | h      | 하 → ha  |

#### Final Consonants

**Phonetic-based:**

| Hangul                     | Roman | Example   |
| :------------------------- | :---- | :-------- |
| ㄱ, ㄲ, ㅋ, ㄳ, ㄺ         | k     | 국 → guk  |
| ㄴ, ㄵ, ㄶ                 | n     | 안 → an   |
| ㄷ, ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅎ | t     | 옷 → ot   |
| ㄹ, ㄼ, ㄽ, ㄾ, ㅀ         | l     | 말 → mal  |
| ㅁ, ㄻ                     | m     | 밤 → bam  |
| ㅂ, ㅄ, ㄿ                 | p     | 밥 → bap  |
| ㅇ                         | ng    | 강 → gang |

**Literal (spelling-based):**

| Hangul | Roman | Example         |
| :----- | :---- | :-------------- |
| ㄱ     | g     | 국 → gug        |
| ㄺ     | lg    | 읽 → ilg        |
| ㄻ     | lm    | 삶 → salm       |
| ㄼ     | lb    | 여덟 → yeodeolb |
| ㄳ     | gs    | 넋 → neogs      |
| ㅄ     | bs    | 값 → gabs       |

### Vowel Romanization

| Hangul | Roman | Example  |
| :----- | :---- | :------- |
| ㅏ     | a     | 아 → a   |
| ㅐ     | ae    | 애 → ae  |
| ㅑ     | ya    | 야 → ya  |
| ㅒ     | yae   | 얘 → yae |
| ㅓ     | eo    | 어 → eo  |
| ㅔ     | e     | 에 → e   |
| ㅕ     | yeo   | 여 → yeo |
| ㅖ     | ye    | 예 → ye  |
| ㅗ     | o     | 오 → o   |
| ㅘ     | wa    | 와 → wa  |
| ㅙ     | wae   | 왜 → wae |
| ㅚ     | oe    | 외 → oe  |
| ㅛ     | yo    | 요 → yo  |
| ㅜ     | u     | 우 → u   |
| ㅝ     | wo    | 워 → wo  |
| ㅞ     | we    | 웨 → we  |
| ㅟ     | wi    | 위 → wi  |
| ㅠ     | yu    | 유 → yu  |
| ㅡ     | eu    | 으 → eu  |
| ㅢ     | ui    | 의 → ui  |
| ㅣ     | i     | 이 → i   |

---

## API Reference

### Core Functions

| Function                       | Description                            | Mode     | Return Type |
| :----------------------------- | :------------------------------------- | :------- | :---------- |
| `romanize(text)`               | Phonetic-based romanization (default)  | Phonetic | `str`       |
| `romanize_pronunciation(text)` | Phonetic-based romanization (explicit) | Phonetic | `str`       |
| `romanize_standard(text)`      | Spelling-based romanization            | Literal  | `str`       |
| `romanize_korean(text)`        | Alias for `romanize()`                 | Phonetic | `str`       |

---

## Advanced Usage

### Batch Processing

```python
from romanization import romanize, romanize_standard

# Process multiple words
words = ["서울", "부산", "대구", "인천", "광주"]
romanized = [romanize(w) for w in words]

for ko, en in zip(words, romanized):
    print(f"{ko} → {en}")

# Output:
# 서울 → seoul
# 부산 → busan
# 대구 → daegu
# 인천 → incheon
# 광주 → gwangju
```

### Name Romanization

```python
from romanization import romanize

# Korean name romanization
names = ["김철수", "이영희", "박민수", "최지은"]
for name in names:
    print(f"{name} → {romanize(name).title()}")

# Output:
# 김철수 → Gimcheolsu
# 이영희 → Iyeonghui
# 박민수 → Bangminsu
# 최지은 → Choejieun
```

---

## Use Case Recommendations

| Use Case                           | Recommended Mode      | Reason                           |
| :--------------------------------- | :-------------------- | :------------------------------- |
| Pronunciation guide for foreigners | `romanize()`          | Closer to actual pronunciation   |
| Passport/Official documents        | `romanize()`          | Standard romanization compliance |
| Database search                    | `romanize_standard()` | Spelling consistency             |
| Academic papers                    | `romanize()`          | International standard           |
| Programming variable names         | `romanize_standard()` | Predictability                   |

---

## Troubleshooting

### FAQ

**Q: I want to add spaces between family name and given name.**
A: Include spaces in the input text: `romanize("김 철수")` → `"gim cheolsu"`

**Q: How do I convert to uppercase?**
A: Use Python string methods:

```python
romanize("한국").upper()  # HANGUK
romanize("한국").title()  # Hanguk
```

**Q: Which mode should I use—phonetic or literal?**
A: Generally, phonetic-based (`romanize()`) is recommended. Use literal mode for database keys or programming identifiers where consistency is important.

---

## Performance

```python
from romanization import romanize
import time

# Benchmark: 10,000 words
words = ["한국어"] * 10000
start = time.time()
results = [romanize(w) for w in words]
elapsed = time.time() - start

print(f"Processing time: {elapsed:.3f}s")
print(f"Speed: {len(words)/elapsed:.0f} words/sec")
# Typically 5,000+ words/sec performance
```

---

## License

This module is distributed under the [MIT License](../../LICENSE).
For contributions and bug reports, please use [GitHub Issues](https://github.com/jake1104/KULIM/issues).

---

<p align="center">
  Part of the KULIM Framework
</p>
