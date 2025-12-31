# KULIM

> **Read in other languages**: [한국어](README.md)

<p align="center">
  <strong>Korean Unified Linguistic Integration Manager</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version 0.1.0">
  <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/rust-accelerated-orange?logo=rust" alt="Rust Accelerated">
  <img src="https://img.shields.io/badge/license-MIT-green?logo=github" alt="MIT License">
</p>

## Introduction

**KULIM** is a unified solution for Korean language processing.
Going beyond a simple morphological analyzer, it aims to be a **comprehensive Korean processing library** covering everything from basic Hangul Jamo processing to high-performance syntax parsing, and in the future, Romanization and pronunciation conversion.

Combining the productivity of Python with the powerful performance of Rust, it can be widely used from precise analysis for research purposes to real-time processing for large-scale services.

## Package Structure

KULIM provides modular packages for each function.

### 1. Hangul (`hangul`)

**Basic Hangul processing package.**

- **Key Features**: Jamo decomposition/composition, Hangul validation, Jongsung (final consonant) check.
- A fast and lightweight pure Python utility module optimized for preprocessing tasks.

### 2. Grammar (`grammar`)

**Core language processing engine.**

- **Key Features**:
  - **Morphological Analysis**: Provides detailed analysis results based on the `Morph` object (surface form, POS, lemma, properties, etc.).
  - **Syntax Parsing**: Dependency parsing and sentence component identification (Subject, Object, Predicate, etc.).
  - **Training System**: Supports CoNLL-U based model training and online learning.
- **Technology**: Transformer + Viterbi hybrid, Rust-accelerated Trie, GPU acceleration support.
- [View Details and Usage](grammar/README.en.md)

## Installation

```bash
# Clone repository and install
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
```

## Core Features Summary

### 1. Morphological Analysis & Classification

The `grammar` package returns analysis results as a list of `Morph` objects with rich attributes, not just plain text.

```python
from grammar import MorphAnalyzer

analyzer = MorphAnalyzer(use_rust=True)
result = analyzer.analyze("친구와 학교에 갔다.")

for m in result:
    print(f"[{m.surface}] POS: {m.pos}, Lemma: {m.lemma}")
    print(f"  - Is Lexical: {m.is_lexical}")
    print(f"  - Is Free: {m.is_free}")
```

### 2. Syntax Parsing

Analyzes the structure of a sentence to identify the syntactic components of each eojeol.

```python
from grammar import SyntaxAnalyzer, MorphAnalyzer

m_analyzer = MorphAnalyzer()
s_analyzer = SyntaxAnalyzer()

# Execute analysis (Word, POS_Sequence, Component)
syntax_result = s_analyzer.analyze(text="나는 밥을 먹었다.", morph_analyzer=m_analyzer)

for word, pos, comp in syntax_result:
    print(f"{word}: {comp.name}")
    # 나: SUBJECT, 밥: OBJECT, 먹었다: PREDICATE
```

### 3. Hangul Jamo Processing

```python
from hangul import decompose_korean, has_jongsung

# Jamo decomposition
print(decompose_korean("한글")) # [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]

# Jongsung check
print(has_jongsung("강")) # True
```

> **For detailed API specifications, please refer to the README of each package.**
>
> - [Grammar Package Detailed Guide](grammar/README.en.md)
> - [Hangul Package Detailed Guide](hangul/README.en.md)

## Version Info

### v0.1.0-rc.9 (Grammar), v0.0.1 (Hangul) (Jan 1, 2026)

- **Experimental Release**
- Hybrid Morphological Analyzer and Rust Acceleration Engine included
- Basic Hangul processing module separated and optimized
- Official support for CLI and Python API

## License

This project follows the **CC BY-SA 4.0** license.
See the [LICENSE](LICENSE.md) file for details.

## Developers

- **Jeongwoo Ahn (jake1104)**
  - GitHub: [@jake1104](https://github.com/jake1104)
  - Contact: [iamjake1104@gmail.com](mailto:iamjake1104@gmail.com)

## Resources

This project uses the [UD Korean Kaist Treebank](https://universaldependencies.org/treebanks/ko_kaist/index.html) from the Universal Dependencies project
, licensed under CC BY-SA 4.0.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jake1104">jake1104</a>
</p>
