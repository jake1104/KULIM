# KULIM

> **다른 언어로 읽기**: [English](README.en.md)

<p align="center">
  <strong>Korean Unified Linguistic Integration Manager</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version 0.1.0">
  <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/rust-accelerated-orange?logo=rust" alt="Rust Accelerated">
  <img src="https://img.shields.io/badge/license-MIT-green?logo=github" alt="MIT License">
</p>

## 소개

**KULIM**은 한국어 처리를 위한 통합 솔루션입니다.
단순한 형태소 분석기를 넘어, 한글 자모 처리부터 고성능 구문 분석, 그리고 미래의 로마자 표기와 발음 변환까지 아우르는 **종합 한국어 처리 라이브러리**을 지향합니다.

Python의 생산성과 Rust의 강력한 성능을 결합하여, 연구 목적의 정밀한 분석부터 대규모 서비스의 실시간 처리까지 폭넓게 활용될 수 있습니다.

## 패키지 구성

KULIM은 기능별로 모듈화된 패키지들을 제공합니다.

### 1. Hangul (`hangul`)

#### v0.0.1

**한글 처리 패키지**입니다.

- **주요 기능**: 자모 분해(Decomposition) 및 결합(Composition), 한글 판별, 종성 유무 확인
- 빠르고 가벼운 순수 유틸리티 모듈로, 전처리 작업에 최적화되어 있습니다.

### 2. Grammar (`grammar`)

#### v0.1.0-rc.1

**핵심 언어 처리 엔진**입니다. 위의 Hangul 패키지 v0.0.1에 의존합니다.

- **주요 기능**: 형태소 분석, 구문 분석(Syntax Parsing), 모델 학습 등을 지원합니다.
- **기술**: Transformer 기반 하이브리드 태깅, Rust 가속 Trie, GPU 가속 지원
- [상세 설명 및 사용법 보러가기](grammar/README.md)

### 개발 예정

다음 기능들이 로드맵에 포함되어 있습니다:

- **로마자 표기 (Romanization)**: 표준 발음법에 따른 로마자 변환 라이브러리
- **발음 변환 (G2P)**: 문맥을 고려한 한국어 발음 표기 생성 자동화

## 설치 방법

```bash
# 저장소 복제 및 설치
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
pip install -e .
```

## 빠른 시작

각 패키지는 독립적으로 또는 통합하여 사용할 수 있습니다.

```python
# 1. Grammar: 형태소 분석
from grammar import MorphAnalyzer
analyzer = MorphAnalyzer()
print(analyzer.analyze("오늘 친구가 학교에 갔다."))

# 2. Hangul: 자모 분해
from hangul import decompose_korean
print(decompose_korean("한글"))
# [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]
```

> **상세한 사용법은 각 패키지의 README를 참조하세요.**
>
> - [Grammar 패키지 가이드](grammar/README.md)

## 버전 정보

### v0.1.0-rc.1 (Grammar), v0.0.1 (Hangul) (2025.12.14)

- **실험적 릴리즈**
- 하이브리드 형태소 분석기 및 Rust 가속 엔진 탑재
- 기초 한글 처리 모듈 분리 및 최적화
- CLI 및 Python API 정식 지원

## 라이선스

이 프로젝트는 **CC BY-SA 4.0** 라이선스를 따릅니다.
자세한 내용은 [LICENSE](LICENSE.md) 파일을 참조하십시오.

## 개발자

- **안정우 (jake1104)**
  - GitHub: [@jake1104](https://github.com/jake1104)
  - 문의: [iamjake1104@gmail.com](mailto:iamjake1104@gmail.com)

# 자료

본 프로젝트는 Universal Dependencies의 [UD Korean Kaist Treebank](https://universaldependencies.org/treebanks/ko_kaist/index.html)를 사용합니다.  
이 데이터는 **CC BY-SA 4.0** 라이선스에 따라 제공됩니다.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jake1104">jake1104</a>
</p>
