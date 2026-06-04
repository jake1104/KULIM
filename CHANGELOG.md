# Changelog

## [0.1.2] - 2026-06-05

### Added
- Dictionary expansion: 250+ nominals (people, places, objects, food, nature, time, abstract, pronouns, numerals), 170+ predicates (verbs, adjectives, auxiliaries, irregular), 72 endings, 38 particles, 62 modifiers, 17 interjections, 28 affixes
- Place name entries: 압구정, 강남, 판교, etc.
- HMMTrainer: Jelinek-Mercer interpolation smoothing (ML 0.6 / suffix 0.3 / char prior 0.1), character-level suffix emission for OOV, add-k smoothing with log-prob storage
- Stemmer: OOV guesser (다→VV, 하다→VV, 스럽→VA), conjugation-based candidate expansion, EF→NNG transition penalty
- Neural trainer: Early stopping (patience=5), linear warmup (10%), gradient clipping (5.0), AdamW optimizer, cosine annealing LR schedule, k-fold cross-validation, GPU pin_memory
- Lightweight neural models: SimpleTagger (96-dim emb, 2-layer Transformer, ~56K params), CharCNN embedding variant
- Conjugation: 여 irregular (하→해), expanded 불규칙 coverage (ㅂ 20, ㄷ 5, ㅅ 5, ㅎ 15, 르 16, 으 9, 여 1)
- ConstraintValidator: 50+ impossible transitions (JKS→JKO, ETN→EF, VV→JKS, etc.)

### Changed
- Scorers: transition backoff rules 14→28 types, COST_OOV 50→30, EF→non-SF penalty 25
- Stemmer: Viterbi DP with 3-way candidate expansion (trie + conjugation + OOV)
- Dictionary: stem auto-registration for VV/VA/VX entries (lemma[:-1])
- Cache invalidation: old .dat/.pkl files force-rebuilt on version mismatch
- Version bumped to 0.1.2 across all packages (grammar, hangul, pronunciation, romanization, kulim)

### Fixed
- Import error: missing NNB, NP, NR, VCN, XPN, XSN, XSA, JKV in dictionary.py
- Romanization: 압구정→apgujeong (proper noun segmentation)
- Dict cache: stale dictionary.dat not reflecting new entries

### Removed
- Conjugation `__main__` test blocks
- Overly verbose debug logging in release path

## [0.1.1] - 2026-05-20

### Added
- .kg model packaging format (KULIM Grammar binary package)
- save_model() / load_model() API
- Rust-accelerated trie search integration
- GPU support (CuPy-based neural inference)
- Syntax analysis with SentenceComponent classification
- Transparent model loading from data directory

### Changed
- Architecture: migrated from flat module structure to pip-installable sub-packages
- Dictionary: SejongDictionary integration as fallback source
- CLI: subcommand-based interface (analyze, train, save, benchmark)

### Fixed
- Pronunciation: ㅇ batchim liaison (잉어→이어), ㄳ residue in aspiration, ㅍ→ㅂ neutralization
- Romanization: tensification with POS awareness for compounds
- Conjugation: compose() empty string argument
- hangul: Compatibility Jamo classification for 0x3165-0x318E range

## [0.1.0] - 2026-05-01

### Added
- Initial release
- Morphological analysis with Viterbi DP + dictionary trie
- Basic conjugation analysis (regular + ㅂ/ㄷ/ㅅ/르/으 irregular)
- Pronunciation engine (standard Korean)
- Romanization (Revised Romanization, phonetic/literal modes)
- hangul module (jamo decompose/compose)
- CLI with analyze/train/benchmark commands
- HMM transition scoring with 6 backoff rules
