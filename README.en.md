# KULIM (Korean Unified Linguistic Integration Manager)

<p align="center">
  <b>English</b> | <a href="README.md">한국어</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/rust-accelerated-orange.svg?style=flat-square&logo=rust" alt="Rust">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/status-experimental-red.svg?style=flat-square" alt="Status">
</p>

---

**KULIM** is a high-performance linguistics processing framework designed for modern Korean language processing.
Going beyond mere text analysis, it aims to be an **integrated solution** covering everything from basic Hangul character handling to deep learning-based precision syntax parsing.

By combining the productivity of Python with the low-level performance of Rust, KULIM meets a wide spectrum of requirements, from large-scale data processing to complex linguistic research.

## Key Features

- **Hybrid Engine**: Morphological analysis combining dictionary-based precision with Transformer-based flexibility.
- **Ultra-fast Performance**: Core algorithms rewritten in Rust for a significant leap in processing speed compared to pure Python engines.
- **Precision Syntax Parsing**: Dependency parsing and sentence component identification following Universal Dependencies standards.
- **Scalability**: GPU acceleration support and real-time model updates via Online Learning APIs.

## Package Roadmap

1.  **[grammar](grammar/)**: Core language analysis engine (morphology, syntax parsing)
2.  **[hangul](hangul/)**: Basic Hangul processing utilities (decomposition, composition, etc.)
3.  **[kulim](kulim/)**: Unified library interface

## Getting Started

KULIM recommends using the modern package manager, `uv`.

```bash
# Clone the repository and set up the environment
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
```

### Basic Usage

```python
from grammar import MorphAnalyzer

# Initialize engine (Enable Rust acceleration)
analyzer = MorphAnalyzer(use_rust=True)

# Run morphological analysis
result = analyzer.analyze("KULIM helps analyze Korean.")
for m in result:
    print(f"{m.surface}/{m.pos}")
```

## Project Status & Disclaimer

While this version (`v0.1.0`) is the first official release of KULIM, it is still considered an **Experimental Release** with ongoing algorithm refinements and data structure optimizations.

> [!WARNING]
>
> - **Zero Warranty**: This software is provided "as is," and the author assumes no legal responsibility for the accuracy of results or any loss incurred through its use.
> - **Breaking Changes**: API specifications may change without notice before reaching the v1.0.0 stable release.
> - **Production Note**: Please conduct thorough validation before introducing this into a production environment.

## Changelog

Detailed version-by-version changes can be found in [CHANGELOG.md](CHANGELOG.md).

## Feedback & Contribution

KULIM is an open-source project and welcomes your contributions.

- **Issues**: Use [GitHub Issues](https://github.com/jake1104/KULIM/issues) for bug reports and feature requests.
- **Contact**: For technical inquiries or collaboration proposals, please reach out to [iamjake1104@gmail.com](mailto:iamjake1104@gmail.com).

## License

This project is licensed under the **MIT License**.
Please also check the license regulations of the dataset used for training ([UD Korean Kaist](https://universaldependencies.org/treebanks/ko_kaist/index.html)).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jake1104">jake1104</a>
</p>
