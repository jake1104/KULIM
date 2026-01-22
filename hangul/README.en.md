# KULIM Hangul

<p align="center">
  <img src="https://img.shields.io/badge/package-hangul-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.0.1-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square&logo=python" alt="Python">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-korean-green.svg?style=flat-square" alt="Korean"></a>
</p>

---

## Overview

**KULIM Hangul** is a lightweight, pure-Python utility package for Hangul processing.
It provides fundamental features such as Jamo decomposition, composition, and Hangul character validation without any external dependencies.

### Key Features

- **Zero Dependency**: Can be immediately integrated without requiring any other libraries.
- **High Performance**: Optimized via bitwise operations on Unicode for high-speed processing of large-scale text.
- **Linguistic Precision**: Fully supports the linguistic distinction between initial, medial, and final consonants (jongsung).

---

## Installation

```bash
# Install as a standalone package
pip install hangul

# Also included in the unified KULIM package
pip install kulim
```

---

## Usage

### 1. Decomposition & Composition

```python
from hangul import decompose, compose, decompose_korean

# Single character decomposition: '한' -> ('ㅎ', 'ㅏ', 'ㄴ')
print(decompose("한"))

# Full string decomposition
print(decompose_korean("한글"))
# [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]

# Composition: ('ㅎ', 'ㅏ', 'ㄴ') -> '한'
print(compose("ㅎ", "ㅏ", "ㄴ"))
```

### 2. Hangul Utilities

```python
from hangul import is_hangul, has_jongsung

# Character validation
print(is_hangul("가"))  # True
print(is_hangul("A"))   # False

# Check for final consonant (jongsung)
print(has_jongsung("국")) # True
print(has_jongsung("가")) # False
```

---

## License

This module is distributed under the [MIT License](../../LICENSE).
Please use [GitHub Issues](https://github.com/jake1104/KULIM/issues) for contributions and bug reports.

---

<p align="center">
  Part of the KULIM Framework
</p>
