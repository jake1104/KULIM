# KULIM Grammar

> **Read in other languages**: [한국어](README.md)

⚠️ **Experimental Version (v0.1.0-rc.1)**

This project is an early-stage analyzer for Korean morphological analysis and syntax parsing.
Accuracy is not guaranteed, and the API and output format are subject to change without notice.

## Key Features

- **Morphological Analysis**:
  - Hybrid tagging combining Deep Learning (Transformer) models and Rule-based dictionaries
  - Robust architecture for handling Out-Of-Vocabulary (OOV) words
- **Syntax Parsing**:
  - Support for Universal Dependencies (CoNLL-U) format
  - Dependency syntax parsing based on morphological analysis results
- **Performance**:
  - **Rust Extension**: Significant speed improvements by implementing core data structures (Trie) and search algorithms in Rust
  - **GPU Acceleration**: High-speed processing of large amounts of data via CuPy-based GPU parallel processing

## Installation

Installed together with the KULIM package. You can optionally enable acceleration modules.

```bash
# Basic Install
pip install kulim

# GPU Acceleration Support (CUDA 12.x)
pip install cupy-cuda12x

# Build Rust Acceleration Module (Install from source)
uv run maturin develop --release -m grammar/rust/Cargo.toml
```

## CLI Usage

You can perform various functions via the `uv run grammar` command in the terminal.

### 1. Sentence Analysis (`analyze`)

```bash
uv run grammar analyze "Today the weather is very nice" [OPTIONS]
```

**Options:**

- `--rust`: Use Rust acceleration
- `--gpu`: Use GPU acceleration
- `--neural`: Use Neural Network model
- `-i, --interactive`: Run in interactive mode

### 2. Model Training (`train`)

Trains the model by taking a file or directory in CoNLL-U format as input.

```bash
uv run grammar train corpus.conllu [OPTIONS]
```

**Options:**

- `--epochs`: Number of training epochs (Default: 10)
- `--batch-size`: Batch size (Default: 32)
- `--device`: `cpu` or `cuda`

### 3. Benchmark (`benchmark`)

Measures system performance.

```bash
uv run grammar benchmark --rust
```

## Python API

How to use as a library in a Python project.

```python
from grammar import MorphAnalyzer

# Initialize Analyzer (Set options)
analyzer = MorphAnalyzer(
    use_rust=True,
    use_gpu=False,
    use_neural=True
)

# Execute Analysis
result = analyzer.analyze("Father goes into the room.")

# Use Result
for word, pos in result:
    print(f"{word}/{pos}")
```

## Rust Module Info

The `grammar/rust` directory contains high-performance extension modules written in Rust.
It uses the Double Array Trie (DAT) algorithm to minimize memory usage and maximize search speed.

### Build Method

```bash
cd grammar/src/grammar/rust
maturin develop --release
```

## Known Limitations

- Proper nouns in Roman alphabet may be segmented by character.
- Predicate derivation via 하다 is partially supported.
- Syntactic labels are incomplete in some constructions.

## Developer Info

- This package is part of the KULIM project.
- For more details, see the [README.md](../../README.en.md) in the parent directory.
