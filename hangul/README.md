# KULIM Hangul

> **다른 언어로 읽기**: [English](README.en.md)

**KULIM Hangul**은 한글 처리를 위한 경량화된 순수 Python 유틸리티 패키지입니다.
자모 분해(Decomposition) 및 결합(Composition), 한글 판별 등의 기초적인 기능을 제공하며, 별도의 의존성 없이 독립적으로 사용할 수 있습니다.

## 설치

KULIM 패키지와 함께 설치되지만, 독립적으로 설치할 수도 있습니다.

```bash
# 독립 설치 (PyPI 배포 시)
pip install hangul

# 소스 설치
pip install -e hangul/
```

## 주요 기능

### 1. 자모 분해 (Decomposition)

한글 글자를 초성, 중성, 종성으로 분리합니다.

```python
from hangul import decompose, decompose_korean

# 단일 문자 분해
print(decompose("글"))
# ('ㄱ', 'ㅡ', 'ㄹ')

# 문자열 전체 분해
print(decompose_korean("한글"))
# [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]
```

### 2. 자모 결합 (Composition)

초성, 중성, 종성을 결합하여 한글 글자를 생성합니다.

```python
from hangul import compose, compose_korean

# 단일 문자 결합
print(compose("ㄱ", "ㅡ", "ㄹ"))
# '글'

# 문자열 전체 결합
chosungs = [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]
print(compose_korean(chosungs))
# '한글'
```

### 3. 유틸리티 (Utilities)

```python
from hangul import is_hangul, has_jongsung

# 한글 여부 확인
print(is_hangul("가"))  # True
print(is_hangul("A"))   # False

# 받침(종성) 유무 확인
print(has_jongsung("감")) # True
print(has_jongsung("가")) # False
```

## 개발자 정보

- 이 패키지는 KULIM 프로젝트의 일부입니다.
- 더 자세한 내용은 상위 디렉토리의 [README.md](../../README.md)를 참조하세요.
