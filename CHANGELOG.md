# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-01-24

### Added

- **grammar v0.1.1**: Custom `.kg` (KULIM Grammar) file format for consolidating 6 model files into single package
- **CLI Save Command**: `uv run grammar save --output <path>` for model packaging
- **Python API**: `MorphAnalyzer.save_model()` and `MorphAnalyzer.load_model()` methods
- **Binary Format Encoder/Decoder**: `kg_format.py` module for custom binary format handling
- **Model Path Parameter**: `MorphAnalyzer(model_path="model.kg")` for loading custom models
- Official release of `grammar` package `v0.1.1`
- Official support for CLI and Python API for the entire workspace
- Hybrid Morphological Analyzer combining Transformer and Viterbi models
- Rust-accelerated Trie for dictionary lookups
- GPU acceleration support for large-scale analysis
- Basic Hangul processing module (`hangul` package `v0.1.0` with Old Hangul support)
- Professional-grade pronunciation engine (`pronunciation` package `v0.1.0`)
- Revised Romanization module (`romanization` package `v0.1.0`) with dual modes (Phonetic/Literal)

### Changed

- Model distribution simplified from 6 separate files to 1 `.kg` file (~120MB)
- Improved documentation with multi-language support (KO/EN)
- Optimized internal package structure for better modularity

### Fixed

- Various minor bugs in morphological analysis and syntax parsing
- Improved stability of the Rust-Python interface

## [grammar 0.1.1] - 2026-01-24

### Added

- **Model Packaging**: Custom `.kg` (KULIM Grammar) file format for consolidating 6 model files into single package
- **CLI Save Command**: `uv run grammar save --output <path>` for model packaging
- **Python API**: `MorphAnalyzer.save_model()` and `MorphAnalyzer.load_model()` methods
- **Binary Format Encoder/Decoder**: `kg_format.py` module for custom binary format handling

### Changed

- Model distribution simplified from 6 separate files to 1 `.kg` file (~120MB)

## [0.1.0] - 2026-01-23

### Added

- Official release of `grammar` package `v0.1.0`.
- Official support for CLI and Python API for the entire workspace.
- Hybrid Morphological Analyzer combining Transformer and Viterbi models.
- Rust-accelerated Trie for dictionary lookups.
- GPU acceleration support for large-scale analysis.
- Basic Hangul processing module (`hangul` package `v0.1.0` with Old Hangul support).
- Professional-grade pronunciation engine (`pronunciation` package `v0.1.0`).
- Revised Romanization module (`romanization` package `v0.1.0`) with dual modes (Phonetic/Literal).

### Changed

- Promoted from release candidate (`0.1.0rc9`) to official release.
- Improved documentation with multi-language support (KO/EN).
- Optimized internal package structure for better modularity.

### Fixed

- Various minor bugs in morphological analysis and syntax parsing.
- Improved stability of the Rust-Python interface.
