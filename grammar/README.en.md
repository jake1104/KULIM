# KULIM Grammar

> **Read in other languages**: [한국어](README.md)

⚠️ **Experimental Version (v0.1.0-rc.4)**

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
uv run grammar analyze "오늘 날씨가 참 좋다" [OPTIONS]
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

## Detailed API Reference

### 1. `Morph` Object (DataClass)

The individual unit of morphological analysis results.

- **Attributes**:

  - `surface` (str): Surface form (e.g., "갔")
  - `pos` (str): POS tag (e.g., "VV")
  - `lemma` (str): Lemma/Base form (e.g., "가다")
  - `score` (float): Analysis score or cost
  - `start`/`end` (int): Start/end position within the sentence
  - `sub_morphs` (List[Morph]): List of sub-morphemes for composite forms

- **Properties**:
  - `is_lexical`: Whether it is a lexical (content) morpheme
  - `is_functional`: Whether it is a functional (grammatical) morpheme
  - `is_free`: Whether it is a free morpheme
  - `is_bound`: Whether it is a bound morpheme
  - `is_composite`: Whether it is a composite morpheme

### 2. `MorphAnalyzer`

- `analyze(text: str) -> List[Morph]`: Analyzes a sentence into morphemes.
- `train(sentence_text, correct_morphemes)`: Performs sentence-level online learning.
- `train_eojeol(surface, morphs)`: Force learns the analysis result for a specific eojeol (e.g., for irregular conjugations).

### 3. `SyntaxAnalyzer`

- `analyze(text: str = None, morphemes: List[Morph] = None, morph_analyzer=None)`:
  - Analyzes sentence components.
  - Return Format: `List[Tuple[word, pos_seq, SentenceComponent]]`
- `SentenceComponent` (Enum):
  - `SUBJECT`, `OBJECT`, `PREDICATE`, `ADVERBIAL`, `DETERMINER`, `COMPLEMENT`, `INDEPENDENT`

### 4. Utility Functions

Used to classify `Morph` objects without needing an analyzer instance.

- `is_lexical_morph(morph)`
- `is_functional_morph(morph) `
- `is_free_morph(morph)`
- `is_bound_morph(morph)`

## Usage Examples

```python
from grammar import MorphAnalyzer, SyntaxAnalyzer

# 1. Initialization
analyzer = MorphAnalyzer(use_rust=True)
syntax = SyntaxAnalyzer()

# 2. Morphological Analysis
morphs = analyzer.analyze("어제는 날씨가 좋았다.")

# 3. Property Classification
for m in morphs:
    if m.is_lexical:
        print(f"Content meaning: {m.surface}")

# 4. Syntax Analysis
results = syntax.analyze(text="친구가 밥을 먹는다.", morph_analyzer=analyzer)
for word, pos, comp in results:
    print(f"{word} -> {comp.name}")
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
