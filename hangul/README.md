# KULIM Hangul

<p align="center">
  <img src="https://img.shields.io/badge/package-hangul-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.0.1-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square&logo=python" alt="Python">
  <a href="README.en.md"><img src="https://img.shields.io/badge/lang-english-green.svg?style=flat-square" alt="English"></a>
</p>

---

## 개요 (Overview)

**KULIM Hangul**은 한글 처리를 위한 경량화된 순수 Python(Pure-Python) 유틸리티 패키지입니다.
한글 전처리의 가장 기본이 되는 자모 분해(Decomposition) 및 결합(Composition), 한글 판별 등의 기능을 외부 의존성 없이 독립적으로 제공합니다.

### 주요 특징

- **Zero Dependency**: 타 라이브러리 의존성 없이 즉시 통합 가능합니다.
- **High Performance**: 유니코드(Unicode) 기반의 최적화된 비트 연산을 통해 대량의 텍스트도 빠르게 처리합니다.
- **Linguistic Precision**: 초성, 중성, 종성(받침)의 언어학적 구분을 완벽하게 지원합니다.

---

## 설치 가이드 (Installation)

```bash
# 독립 패키지로 설치
pip install hangul

# KULIM 통합 패키지에 포함되어 있습니다
pip install kulim
```

---

## 주요 기능 및 사용법 (Usage)

### 1. 자모 분해 및 결합

```python
from hangul import decompose, compose, decompose_korean

# 단일 글자 분해: '한' -> ('ㅎ', 'ㅏ', 'ㄴ')
print(decompose("한"))

# 문자열 전체 분해
print(decompose_korean("한글"))
# [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]

# 자모 결합: ('ㅎ', 'ㅏ', 'ㄴ') -> '한'
print(compose("ㅎ", "ㅏ", "ㄴ"))
```

### 2. 한글 유틸리티

```python
from hangul import is_hangul, has_jongsung

# 한글 글자 판별
print(is_hangul("가"))  # True
print(is_hangul("A"))   # False

# 받침(종성) 유무 확인
print(has_jongsung("국")) # True
print(has_jongsung("가")) # False
```

---

## 라이선스 (License)

본 모듈은 [MIT License](../../LICENSE)에 따라 배포됩니다.
공헌 및 버그 제보는 [GitHub Issues](https://github.com/jake1104/KULIM/issues)를 이용해 주시기 바랍니다.

---

<p align="center">
  Part of the KULIM Framework
</p>
