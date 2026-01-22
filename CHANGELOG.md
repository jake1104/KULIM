# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-23

### Added

- Official release of `grammar` package `v0.1.0`.
- Official support for CLI and Python API for the entire workspace.
- Hybrid Morphological Analyzer combining Transformer and Viterbi models.
- Rust-accelerated Trie for dictionary lookups.
- GPU acceleration support for large-scale analysis.
- Basic Hangul processing module (`hangul` package `v0.0.1`).

### Changed

- Promoted from release candidate (`0.1.0rc9`) to official release.
- Improved documentation with multi-language support (KO/EN).
- Optimized internal package structure for better modularity.

### Fixed

- Various minor bugs in morphological analysis and syntax parsing.
- Improved stability of the Rust-Python interface.
