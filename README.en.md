# KULIM (Korean Unified Linguistic Integration Manager)

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.2-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/rust-accelerated-orange.svg?style=flat-square&logo=rust" alt="Rust">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License">
</p>

<p align="center">
  <b>English</b> | <a href="README.md">한국어</a>
</p>

KULIM is a Korean language processing framework providing morphological analysis, pronunciation conversion, and romanization.

## Packages

| Package | Version | Description |
|---------|---------|-------------|
| [grammar](grammar/) | 0.1.2 | Morphological and syntax analysis engine |
| [hangul](hangul/) | 0.1.2 | Hangul processing utilities (jamo decomposition/composition) |
| [pronunciation](pronunciation/) | 0.1.2 | Standard pronunciation conversion |
| [romanization](romanization/) | 0.1.2 | Korean romanization (phonetic/literal modes) |
| [kulim](kulim/) | 0.1.2 | Unified library interface |

## Quick Start

```bash
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
```

```python
from grammar import MorphAnalyzer
from pronunciation import pronounce
from romanization import romanize, romanize_standard

analyzer = MorphAnalyzer(use_rust=True)
result = analyzer.analyze("KULIM으로 한국어를 분석합니다.")
for m in result:
    print(f"{m.surface}/{m.pos}")

print(pronounce("값있는"))
print(romanize("읽고"))
print(romanize_standard("읽고"))
```

## Requirements

- Python 3.11+
- Rust toolchain (optional, for accelerated trie search)
- CUDA 12.x (optional, for GPU-accelerated neural models)

## License

MIT License. The training dataset (UD Korean Kaist) has its own license terms.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
