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

#### v0.0.1

**Hangul Processing Package**.

- **Key Features**: Jamo Decomposition and Composition, Hangul validation, Check for Jongsung (final consonant)
- It is a fast and lightweight pure utility module optimized for preprocessing tasks.

### 2. Grammar (`grammar`)

#### v0.1.0-rc.1

**Core Language Processing Engine**. Depends on the Hangul package v0.0.1 above.

- **Key Features**: Supports Morphological Analysis, Syntax Parsing, and Model Training.
- **Technology**: Transformer-based hybrid tagging, Rust-accelerated Trie, GPU acceleration support
- [View Details and Usage](grammar/README.en.md)

### Future Development

The following features are included in the roadmap:

- **Romanization**: Standard Romanization library based on standard pronunciation rules
- **G2P (Grapheme-to-Phoneme)**: Automated generation of Korean pronunciation notation considering context

## Installation

```bash
# Clone repository and install
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
pip install -e .
```

## Quick Start

Each package can be used independently or integrated.

```python
# 1. Grammar: Morphological Analysis
from grammar import MorphAnalyzer
analyzer = MorphAnalyzer()
print(analyzer.analyze("Today, a friend went to school."))

# 2. Hangul: Jamo Decomposition
from hangul import decompose_korean
print(decompose_korean("Hangul"))
# [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]
```

> **For detailed usage, please refer to the README of each package.**
>
> - [Grammar Package Guide](grammar/README.en.md)

## Version Info

### v0.1.0-rc.1 (Grammar), v0.0.1 (Hangul) (Dec 14, 2025)

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

# resource

This project uses the [UD Korean Kaist Treebank](https://universaldependencies.org/treebanks/ko_kaist/index.html) from the Universal Dependencies project
, licensed under CC BY-SA 4.0.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jake1104">jake1104</a>
</p>
