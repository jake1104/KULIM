# KULIM

> **다른 언어로 읽기**: [English](README.en.md)

<p align="center">
  <strong>Korean Unified Linguistic Integration Manager</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version 0.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue?logo=python" alt="Python 3.8+">
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

**한글 기초 처리 패키지**입니다.

- **주요 기능**: 자모 분해(Decomposition) 및 결합(Composition), 한글 여부 판별, 종성 유무 확인
- 빠르고 가벼운 순수 Python 유틸리티 모듈로, 전처리 작업에 최적화되어 있습니다.

### 2. Grammar (`grammar`)

**핵심 언어 처리 엔진**입니다.

- **주요 기능**:
  - **형태소 분석**: `Morph` 객체 기반의 상세 분석 결과 제공 (표면형, 품사, 기본형, 속성 등)
  - **구문 분석**: 의존 구문 분석 및 문장 성분(주어, 목적어, 서술어 등) 판별
  - **학습 시스템**: CoNLL-U 기반 모델 학습 및 온라인 추가 학습 지원
- **기술**: Transformer + Viterbi 하이브리드, Rust 가속 Trie, GPU 가속 지원
- [상세 설명 및 사용법 보러가기](grammar/README.md)

## 설치 방법

```bash
# 저장소 복제 및 설치
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
```

## 주요 기능 요약

### 1. 형태소 분석 및 속성 판별

`grammar` 패키지는 분석 결과를 단순히 텍스트로 돌려주는 것이 아니라, 풍부한 속성을 가진 `Morph` 객체 리스트로 반환합니다.

```python
from grammar import MorphAnalyzer

analyzer = MorphAnalyzer(use_rust=True)
result = analyzer.analyze("친구와 학교에 갔다.")

for m in result:
    print(f"[{m.surface}] 품사: {m.pos}, 기본형: {m.lemma}")
    print(f"  - 실질형태소 여부: {m.is_lexical}")
    print(f"  - 자립형태소 여부: {m.is_free}")
```

### 2. 구문 분석 (Syntax Parsing)

문장의 구조를 분석하여 각 어절의 문장 성분을 판별합니다.

```python
from grammar import SyntaxAnalyzer, MorphAnalyzer

m_analyzer = MorphAnalyzer()
s_analyzer = SyntaxAnalyzer()

# 분석 실행 (Word, POS_Sequence, Component)
syntax_result = s_analyzer.analyze(text="나는 밥을 먹었다.", morph_analyzer=m_analyzer)

for word, pos, comp in syntax_result:
    print(f"{word}: {comp.name}")
    # 나: SUBJECT, 밥: OBJECT, 먹었다: PREDICATE
```

### 3. 한글 자모 처리

```python
from hangul import decompose_korean, has_jongsung

# 자모 분해
print(decompose_korean("한글")) # [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]

# 종성 확인
print(has_jongsung("강")) # True
```

> **상세한 API 명세는 각 패키지의 README를 참조하세요.**
>
> - [Grammar 패키지 상세 가이드](grammar/README.md)
> - [Hangul 패키지 상세 가이드](hangul/README.md)

## 버전 정보

### v0.1.0-rc.9 (Grammar), v0.0.1 (Hangul) (2026.1.1)

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

## 자료 (Resources)

본 프로젝트는 Universal Dependencies의 [UD Korean Kaist Treebank](https://universaldependencies.org/treebanks/ko_kaist/index.html)를 사용합니다.  
이 데이터는 **CC BY-SA 4.0** 라이선스에 따라 제공됩니다.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jake1104">jake1104</a>
</p>
