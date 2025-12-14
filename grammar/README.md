# KULIM Grammar

> **다른 언어로 읽기**: [English](README.en.md)

⚠️ **실험적 버전 (v0.1.0-rc.1)**

본 프로젝트는 한국어 형태소 분석 및 구문 분석을 위한 초기 단계의 분석기입니다.
정확도는 보장되지 않으며, API와 출력 형식은 예고 없이 변경될 수 있습니다.

## 주요 특징

- **형태소 분석 (Morphological Analysis)**:
  - 딥러닝(Transformer) 모델과 규칙(Rule-based) 사전을 결합한 하이브리드 태깅
  - 미등록 단어(OOV) 처리에 강건한 아키텍처
- **구문 분석 (Syntax Parsing)**:
  - Universal Dependencies (CoNLL-U) 형식 지원
  - 형태소 분석 결과 기반의 의존 구문 분석
- **성능 가속 (Performance)**:
  - **Rust Extension**: 핵심 자료구조(Trie) 및 검색 알고리즘을 Rust로 구현하여 비약적인 속도 향상
  - **GPU Acceleration**: CuPy 기반의 GPU 병렬 처리를 통해 대용량 데이터 고속 처리

## 설치

KULIM 패키지와 함께 설치됩니다. 선택적으로 가속 모듈을 활성화할 수 있습니다.

```bash
# 기본 설치
pip install kulim

# GPU 가속 지원 (CUDA 12.x)
pip install cupy-cuda12x

# Rust 가속 모듈 빌드 (소스 설치 시)
uv run maturin develop --release -m grammar/rust/Cargo.toml
```

## CLI 사용법

터미널에서 `uv run grammar` 명령을 통해 다양한 기능을 수행할 수 있습니다.

### 1. 문장 분석 (`analyze`)

```bash
uv run grammar analyze "오늘 날씨가 참 좋다" [OPTIONS]
```

**옵션:**

- `--rust`: Rust 가속 사용
- `--gpu`: GPU 가속 사용
- `--neural`: 신경망 모델 사용
- `-i, --interactive`: 대화형 모드 실행

### 2. 모델 학습 (`train`)

CoNLL-U 형식의 파일이나 디렉토리를 입력받아 모델을 학습시킵니다.

```bash
uv run grammar train corpus.conllu [OPTIONS]
```

**옵션:**

- `--epochs`: 학습 에포크 수 (기본: 10)
- `--batch-size`: 배치 크기 (기본: 32)
- `--device`: `cpu` 또는 `cuda`

### 3. 벤치마크 (`benchmark`)

시스템 성능을 측정합니다.

```bash
uv run grammar benchmark --rust
```

## Python API

Python 프로젝트에서 라이브러리로 사용하는 방법입니다.

```python
from grammar import MorphAnalyzer

# 분석기 초기화 (옵션 설정)
analyzer = MorphAnalyzer(
    use_rust=True,
    use_gpu=False,
    use_neural=True
)

# 분석 실행
result = analyzer.analyze("아버지가 방에 들어가신다.")

# 결과 활용
for word, pos in result:
    print(f"{word}/{pos}")
```

## Rust 모듈 정보

`grammar/rust` 디렉토리는 Rust로 작성된 고성능 확장 모듈을 포함합니다.
Double Array Trie (DAT) 알고리즘을 사용하여 메모리 사용량을 최소화하고 검색 속도를 극대화했습니다.

### 빌드 방법

```bash
cd grammar/src/grammar/rust
maturin develop --release
```

## 알려진 한계

- 로마자(알파벳)로 된 고유명사는 문자 단위로 분절될 수 있습니다.
- `하다`를 통한 술어 파생은 부분적으로만 지원됩니다.
- 일부 구문 구조에서 구문 레이블이 완전하지 않을 수 있습니다.

## 개발자 정보

- 이 패키지는 KULIM 프로젝트의 일부입니다.
- 더 자세한 내용은 상위 디렉토리의 [README.md](../../README.md)를 참조하세요.
