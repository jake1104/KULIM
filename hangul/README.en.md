# KULIM Hangul

> **Read in other languages**: [한국어](README.md)

**KULIM Hangul** is a lightweight, pure Python utility package for Hangul processing.
It provides basic functions such as Jamo Decomposition and Composition, and Hangul validation, and can be used independently without separate dependencies.

## Installation

It is installed with the KULIM package, but can also be installed independently.

```bash
# Independent Install (When distributed on PyPI)
pip install hangul

# Install from source
pip install -e hangul/
```

## Key Features

### 1. Jamo Decomposition

Separates Hangul characters into Initial (Choseong), Medial (Jungseong), and Final (Jongseong) consonants.

```python
from hangul import decompose, decompose_korean

# Single character decomposition
print(decompose("글"))
# ('ㄱ', 'ㅡ', 'ㄹ')

# String decomposition
print(decompose_korean("한글"))
# [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]
```

### 2. Jamo Composition

Combines Initial, Medial, and Final consonants to create Hangul characters.

```python
from hangul import compose, compose_korean

# Single character composition
print(compose("ㄱ", "ㅡ", "ㄹ"))
# '글'

# String composition
chosungs = [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]
print(compose_korean(chosungs))
# '한글'
```

### 3. Utilities

```python
from hangul import is_hangul, has_jongsung

# Check if Hangul
print(is_hangul("가"))  # True
print(is_hangul("A"))   # False

# Check for Jongsung (Final Consonant)
print(has_jongsung("감")) # True
print(has_jongsung("가")) # False
```

## Developer Info

- This package is part of the KULIM project.
- For more details, see the [README.md](../../README.en.md) in the parent directory.
