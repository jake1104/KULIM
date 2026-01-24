# KULIM Pronunciation

<p align="center">
  <img src="https://img.shields.io/badge/package-pronunciation-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.1.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-korean-green.svg?style=flat-square" alt="Korean"></a>
</p>

---

## Overview

**KULIM Pronunciation** is a high-performance engine for Korean standard pronunciation conversion.
Designed based on the National Institute of Korean Language's standard pronunciation rules, it provides accurate pronunciation conversion through a systematic pipeline architecture that applies complex phonological rules.

### Key Features

- **Pipeline Architecture**: Extensible structure through modular Rule classes
- **Phonological Rules**: Implementation of major phonological rules including aspiration, palatalization, liaison, tensification, nasalization, and liquidization
- **Context-Aware**: Context-based tensification processing through original final consonant tracking
- **Standard Compliance**: Adherence to Standard Korean Language Dictionary pronunciation rules

---

## Installation

```bash
# Install as standalone package
pip install pronunciation

# Included in KULIM integrated package
pip install kulim
```

**Dependencies:**

- `hangul`: Jamo decomposition/composition functionality

---

## Usage

### 1. Basic Pronunciation Conversion

```python
from pronunciation import pronounce

# Basic usage
result = pronounce("밥이")
print(result)  # 바비

# Complex phonological changes
print(pronounce("국민"))    # 궁민 (Nasalization)
print(pronounce("독립"))    # 동닙 (Nasalization)
print(pronounce("같이"))    # 가치 (Palatalization)
print(pronounce("놓고"))    # 노코 (Aspiration)
```

### 2. Advanced Phonological Rules

```python
from pronunciation import pronounce

# Liaison
print(pronounce("밥이"))    # 바비
print(pronounce("옷을"))    # 오슬
print(pronounce("값이"))    # 갑씨 (Cluster simplification + Liaison)

# Tensification
print(pronounce("국밥"))    # 국빱 (Post-obstruent tensification)
print(pronounce("읽고"))    # 일꼬 (Cluster + Tensification)
print(pronounce("앉다"))    # 안따 (Verb stem tensification)

# H-deletion and Aspiration
print(pronounce("싫어"))    # 시러 (ㅎ deletion)
print(pronounce("좋다"))    # 조타 (ㅎ + ㄷ -> ㅌ)
print(pronounce("놓고"))    # 노코 (ㅎ + ㄱ -> ㅋ)

# Palatalization
print(pronounce("같이"))    # 가치 (ㄷ + 이 -> 지)
print(pronounce("굳이"))    # 구지
print(pronounce("해돋이"))  # 해도지
```

### 3. Sentence-level Processing

```python
from pronunciation import pronounce

sentence = "오늘 날씨가 정말 좋네요"
result = pronounce(sentence)
print(result)  # 오늘 날씨가 정말 존네요

# Complex phonological changes
text = "국립중앙박물관"
print(pronounce(text))  # 궁님중앙방물관
```

---

## Architecture

### Pipeline Pattern

The Pronunciation engine consists of the following rule pipeline:

```
Input Text
    ↓
[1] Aspiration Rule
    ↓
[2] Palatalization Rule
    ↓
[3] Liaison Rule
    ↓
[4] Normalization Rule
    ↓
[5] Tensification Rule
    ↓
[6] Assimilation Rule
    ↓
Output Pronunciation
```

### Rule Execution Order

The execution order of rules is **strictly** determined by phonological priority:

1. **Aspiration**: `ㅎ` + obstruent → aspirated (e.g., `놓고` → `노코`)
2. **Palatalization**: `ㄷ/ㅌ` + `이` → `지/치` (e.g., `같이` → `가치`)
3. **Liaison**: Final consonant → next syllable initial (e.g., `밥이` → `바비`)
4. **Neutralization**: Final consonant simplification to 7 representative sounds
5. **Tensification**: Plain consonant → tense after obstruent (e.g., `국밥` → `국빱`)
6. **Assimilation**: Nasalization, liquidization (e.g., `국민` → `궁민`)

---

## API Reference

### Core Functions

| Function                 | Description                            | Return Type |
| :----------------------- | :------------------------------------- | :---------- |
| `pronounce(text)`        | Convert text to standard pronunciation | `str`       |
| `pronounce_korean(text)` | Alias for `pronounce()`                | `str`       |

### PronunciationEngine

Engine class for advanced users:

```python
from pronunciation import PronunciationEngine

# Create custom engine
engine = PronunciationEngine()

# Convert pronunciation
result = engine.pronounce("한국어")
print(result)  # 한구거
```

---

## Implemented Phonological Rules

### ✅ Fully Implemented

| Rule                       | Description                                                | Example                      |
| :------------------------- | :--------------------------------------------------------- | :--------------------------- |
| **Neutralization**         | Final consonant simplification to 7 representative sounds  | `옷` → `옫` (ㅅ→ㄷ)          |
| **Cluster Simplification** | Complex final consonant simplification (context-dependent) | `값` → `갑`, `읽고` → `일꼬` |
| **Liaison**                | Final consonant moves to next syllable initial             | `밥이` → `바비`              |
| **ㅎ Deletion**            | ㅎ disappears in certain environments                      | `싫어` → `시러`              |
| **Aspiration**             | ㅎ + obstruent → aspirated                                 | `놓고` → `노코`              |
| **Palatalization**         | ㄷ/ㅌ + 이 → 지/치                                         | `같이` → `가치`              |
| **Tensification**          | Plain → tense after obstruent                              | `국밥` → `국빱`              |
| **Nasalization**           | Obstruent + nasal → nasal + nasal                          | `국민` → `궁민`              |
| **Liquidization**          | ㄴ + ㄹ / ㄹ + ㄴ → ㄹ + ㄹ                                | `신라` → `실라`              |

### 🚧 Planned for Future

- **N-insertion**: `솜이불` → `솜니불`
- **Sai-siot**: `나뭇가지` → `나문가지`
- **Vowel harmony**: `가아` → `가`
- **의 pronunciation**: `민주주의의` → `민주주이에`

---

## Advanced Usage

### Batch Processing

```python
from pronunciation import pronounce

texts = [
    "안녕하세요",
    "반갑습니다",
    "좋은 하루 되세요"
]

results = [pronounce(text) for text in texts]
for original, pronounced in zip(texts, results):
    print(f"{original} → {pronounced}")
```

### Pronunciation Comparison Analysis

```python
from pronunciation import pronounce

def analyze_pronunciation(word):
    """Compare and analyze original vs pronunciation"""
    pronunciation = pronounce(word)
    if word == pronunciation:
        print(f"✓ {word}: No pronunciation change")
    else:
        print(f"→ {word} → {pronunciation}")

        # Analyze changes
        if len(word) == len(pronunciation):
            for i, (o, p) in enumerate(zip(word, pronunciation)):
                if o != p:
                    print(f"  Position {i+1}: '{o}' → '{p}'")

# Usage example
analyze_pronunciation("국민")
# → 국민 → 궁민
#   Position 1: '국' → '궁'
```

---

## Performance

### Benchmark

```python
from pronunciation import pronounce
import time

# Benchmark: 10,000 words
words = ["한국어"] * 10000
start = time.time()
results = [pronounce(w) for w in words]
elapsed = time.time() - start

print(f"Processing time: {elapsed:.3f}s")
print(f"Speed: {len(words)/elapsed:.0f} words/sec")
# Typically 10,000+ words/sec performance
```

---

## Troubleshooting

### FAQ

**Q: Some word pronunciations differ from expectations.**
A: The current version operates without morpheme boundary information, so some tensification rules may not be accurate. Example: `신고` (wearing shoes vs. reporting)

**Q: Sai-siot rules are not applied.**
A: Sai-siot rules are planned for v0.2.0. Rules requiring compound noun analysis are currently not implemented.

**Q: Can pronunciation conversion speed be improved?**
A: For bulk processing, use list comprehensions, or use the future Rust-ported version.

---

## Contributing

To add new phonological rules:

1. Create a new rule class in `pronunciation/src/pronunciation/rules/`
2. Inherit from `PronunciationRule` abstract class
3. Implement `apply()` method
4. Add rule to pipeline in `engine.py` (mind the order!)

---

## License

This module is distributed under the [MIT License](../../LICENSE).
For contributions and bug reports, please use [GitHub Issues](https://github.com/jake1104/KULIM/issues).

---

<p align="center">
  Part of the KULIM Framework
</p>
