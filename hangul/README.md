# KULIM Hangul

<p align="center">
  <img src="https://img.shields.io/badge/package-hangul-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.1.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <a href="README.en.md"><img src="https://img.shields.io/badge/lang-english-green.svg?style=flat-square" alt="English"></a>
</p>

---

## 개요 (Overview)

**KULIM Hangul**은 한글 처리를 위한 경량화된 순수 Python 유틸리티 패키지입니다.
한글 전처리의 가장 기본이 되는 자모 분해(Decomposition) 및 결합(Composition), 한글 판별 등의 기능을 외부 의존성 없이 독립적으로 제공합니다.

### 주요 특징

- **Zero Dependency**: 타 라이브러리 의존성 없이 즉시 통합 가능합니다.
- **Old Hangul Support**: 옛한글(Old Hangul) 및 확장 자모 영역을 완벽하게 지원합니다.
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
cho, jung, jong = decompose("한")
print(f"초성: {cho}, 중성: {jung}, 종성: {jong}")
# 출력: 초성: ㅎ, 중성: ㅏ, 종성: ㄴ

# 문자열 전체 분해
result = decompose_korean("한글")
print(result)
# 출력: [('ㅎ', 'ㅏ', 'ㄴ'), ('ㄱ', 'ㅡ', 'ㄹ')]

# 자모 결합: ('ㅎ', 'ㅏ', 'ㄴ') -> '한'
char = compose("ㅎ", "ㅏ", "ㄴ")
print(char)  # 출력: 한

# 복합 자모 처리
cho, jung, jong = decompose("값")
print(f"{cho}, {jung}, {jong}")  # 출력: ㄱ, ㅏ, ㅄ
```

### 2. 한글 유틸리티

```python
from hangul import is_hangul, has_jongsung

# 한글 글자 판별 (현대 한글 + 옛한글)
print(is_hangul("가"))   # True
print(is_hangul("A"))    # False
print(is_hangul("\u1100"))  # True (옛한글 초성 ᄀ)

# 받침(종성) 유무 확인
print(has_jongsung("국"))  # True
print(has_jongsung("가"))  # False
print(has_jongsung("값"))  # True (복합 종성 ㅄ)
```

### 3. 옛한글 (Old Hangul) 지원

v0.1.0부터 확장 자모 영역을 지원합니다.

```python
from hangul import is_hangul, decompose

# 옛한글 자모 인식
old_cho = "\u1100"  # ᄀ (Hangul Jamo)
old_jung = "\uA960"  # ꥠ (Hangul Jamo Extended-A)
old_jong = "\uD7B0"  # ힰ (Hangul Jamo Extended-B)

print(is_hangul(old_cho))   # True
print(is_hangul(old_jung))  # True
print(is_hangul(old_jong))  # True

# 옛한글 자모 분해 (비조합형)
cho, jung, jong = decompose(old_cho)
print(cho)  # ᄀ (초성 위치에 반환)
```

**지원 유니코드 범위:**

- Hangul Syllables: `0xAC00-0xD7A3` (현대 한글)
- Hangul Jamo: `0x1100-0x11FF` (옛한글 자모)
- Hangul Jamo Extended-A: `0xA960-0xA97F`
- Hangul Jamo Extended-B: `0xD7B0-0xD7FF`

---

## API 레퍼런스 (API Reference)

### 핵심 함수

| 함수                          | 설명                                  | 반환 타입                    |
| :---------------------------- | :------------------------------------ | :--------------------------- |
| `decompose(char)`             | 한글 음절을 초성, 중성, 종성으로 분해 | `tuple[str, str, str]`       |
| `compose(cho, jung, jong="")` | 자모를 결합하여 한글 음절 생성        | `str`                        |
| `decompose_korean(text)`      | 문자열 전체를 자모 단위로 분해        | `list[tuple[str, str, str]]` |
| `compose_korean(jamos)`       | 자모 리스트를 한글 문자열로 결합      | `str`                        |
| `is_hangul(char)`             | 한글 문자 여부 판별 (옛한글 포함)     | `bool`                       |
| `has_jongsung(char)`          | 종성(받침) 존재 여부 확인             | `bool`                       |

### 상수 (Constants)

```python
from hangul import CHOSUNG, JUNGSUNG, JONGSUNG

# 초성 리스트 (19개)
print(len(CHOSUNG))  # 19
print(CHOSUNG[0])    # 'ㄱ'

# 중성 리스트 (21개)
print(len(JUNGSUNG))  # 21
print(JUNGSUNG[0])    # 'ㅏ'

# 종성 리스트 (28개, 빈 종성 포함)
print(len(JONGSUNG))  # 28
print(JONGSUNG[0])    # '' (빈 종성)
print(JONGSUNG[1])    # 'ㄱ'
```

---

## 고급 사용 예제 (Advanced Usage)

### 초성 검색 (Chosung Search)

```python
from hangul import decompose

def get_chosung(text):
    """텍스트의 초성만 추출"""
    result = []
    for char in text:
        if ord('가') <= ord(char) <= ord('힣'):
            cho, _, _ = decompose(char)
            result.append(cho)
        else:
            result.append(char)
    return ''.join(result)

# 초성 검색 인덱싱
print(get_chosung("안녕하세요"))  # ㅇㄴㅎㅅㅇ
print(get_chosung("대한민국"))    # ㄷㅎㅁㄱ
```

### 자모 정규화

```python
from hangul import decompose, compose

def normalize_jamo(text):
    """복합 자모를 단일 자모로 정규화"""
    result = []
    for char in text:
        if ord('가') <= ord(char) <= ord('힣'):
            cho, jung, jong = decompose(char)
            # 복합 종성 처리 예: ㄳ -> ㄱ
            if jong in ['ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ']:
                jong = jong[0]  # 첫 번째 자음만 사용
            result.append(compose(cho, jung, jong))
        else:
            result.append(char)
    return ''.join(result)

print(normalize_jamo("값"))  # 갑
print(normalize_jamo("닭"))  # 닥
```

---

## 성능 최적화 (Performance)

### 대량 텍스트 처리

```python
from hangul import decompose_korean
import time

# 10만 글자 처리 벤치마크
text = "한글" * 50000
start = time.time()
result = decompose_korean(text)
elapsed = time.time() - start

print(f"처리 시간: {elapsed:.3f}초")
print(f"처리 속도: {len(text)/elapsed:.0f} 글자/초")
# 일반적으로 100,000+ 글자/초 성능
```

---

## 트러블슈팅 (Troubleshooting)

### 자주 묻는 질문 (FAQ)

**Q: 옛한글 자모가 제대로 표시되지 않습니다.**
A: 터미널 폰트가 옛한글 유니코드 범위를 지원하는지 확인하세요. `Noto Sans CJK` 또는 `나눔고딕코딩` 폰트를 권장합니다.

**Q: `compose()` 함수가 빈 문자열을 반환합니다.**
A: 입력한 자모가 유효한 조합인지 확인하세요. 예를 들어, `compose("ㅏ", "ㅏ", "")`는 유효하지 않습니다.

**Q: 복합 종성(예: ㄳ, ㄺ)을 개별 자음으로 분리할 수 있나요?**
A: 현재 버전에서는 복합 종성을 단일 문자열로 반환합니다. 개별 분리가 필요한 경우 별도의 매핑 테이블을 사용하세요.

---

## 라이선스 (License)

본 모듈은 [MIT License](../../LICENSE)에 따라 배포됩니다.
공헌 및 버그 제보는 [GitHub Issues](https://github.com/jake1104/KULIM/issues)를 이용해 주시기 바랍니다.

---

<p align="center">
  Part of the KULIM Framework
</p>
