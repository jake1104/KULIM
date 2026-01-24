# KULIM Pronunciation

<p align="center">
  <img src="https://img.shields.io/badge/package-pronunciation-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.1.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
</p>

---

## 개요 (Overview)

**KULIM Pronunciation**은 한국어 표준 발음 변환을 위한 고성능 엔진입니다.
국립국어원의 표준 발음 규정을 기반으로 설계된 파이프라인 아키텍처를 통해, 복잡한 음운 규칙을 체계적으로 적용하여 정확한 발음 변환을 제공합니다.

### 주요 특징

- **Pipeline Architecture**: 모듈화된 규칙(Rule) 클래스를 통한 확장 가능한 구조
- **Phonological Rules**: 격음화, 구개음화, 연음, 경음화, 비음화, 유음화 등 주요 음운 규칙 구현
- **Context-Aware**: 원본 종성 추적을 통한 문맥 기반 경음화 처리
- **Standard Compliance**: 표준국어대사전 발음 규정 준수

---

## 설치 가이드 (Installation)

```bash
# 독립 패키지로 설치
pip install pronunciation

# KULIM 통합 패키지에 포함되어 있습니다
pip install kulim
```

**의존성:**

- `hangul`: 자모 분해/결합 기능

---

## 주요 기능 및 사용법 (Usage)

### 1. 기본 발음 변환

```python
from pronunciation import pronounce

# 기본 사용
result = pronounce("밥이")
print(result)  # 바비

# 복잡한 음운 변화
print(pronounce("국민"))    # 궁민 (비음화)
print(pronounce("독립"))    # 동닙 (비음화)
print(pronounce("같이"))    # 가치 (구개음화)
print(pronounce("놓고"))    # 노코 (격음화)
```

### 2. 고급 음운 규칙

```python
from pronunciation import pronounce

# 연음 (Liaison)
print(pronounce("밥이"))    # 바비
print(pronounce("옷을"))    # 오슬
print(pronounce("값이"))    # 갑씨 (자음군 단순화 + 연음)

# 경음화 (Tensification)
print(pronounce("국밥"))    # 국빱 (장애음 뒤 경음화)
print(pronounce("읽고"))    # 일꼬 (자음군 + 경음화)
print(pronounce("앉다"))    # 안따 (용언 어간 경음화)

# H-탈락 및 격음화
print(pronounce("싫어"))    # 시러 (ㅎ 탈락)
print(pronounce("좋다"))    # 조타 (ㅎ + ㄷ -> ㅌ)
print(pronounce("놓고"))    # 노코 (ㅎ + ㄱ -> ㅋ)

# 구개음화 (Palatalization)
print(pronounce("같이"))    # 가치 (ㄷ + 이 -> 지)
print(pronounce("굳이"))    # 구지
print(pronounce("해돋이"))  # 해도지
```

### 3. 문장 단위 처리

```python
from pronunciation import pronounce

sentence = "오늘 날씨가 정말 좋네요"
result = pronounce(sentence)
print(result)  # 오늘 날씨가 정말 존네요

# 복합 음운 변화
text = "국립중앙박물관"
print(pronounce(text))  # 궁님중앙방물관
```

---

## 아키텍처 (Architecture)

### Pipeline Pattern

Pronunciation 엔진은 다음과 같은 규칙 파이프라인으로 구성됩니다:

```
Input Text
    ↓
[1] Aspiration Rule (격음화)
    ↓
[2] Palatalization Rule (구개음화)
    ↓
[3] Liaison Rule (연음 & ㅎ 탈락)
    ↓
[4] Normalization Rule (음절말 중화)
    ↓
[5] Tensification Rule (경음화)
    ↓
[6] Assimilation Rule (비음화/유음화)
    ↓
Output Pronunciation
```

### 규칙 실행 순서

규칙의 실행 순서는 음운론적 우선순위에 따라 **엄격하게** 정해져 있습니다:

1. **격음화 (Aspiration)**: `ㅎ` + 장애음 → 격음 (예: `놓고` → `노코`)
2. **구개음화 (Palatalization)**: `ㄷ/ㅌ` + `이` → `지/치` (예: `같이` → `가치`)
3. **연음 (Liaison)**: 종성 → 다음 음절 초성 (예: `밥이` → `바비`)
4. **음절말 중화 (Neutralization)**: 종성 7개 대표음으로 단순화
5. **경음화 (Tensification)**: 장애음 뒤 평음 → 경음 (예: `국밥` → `국빱`)
6. **자음 동화 (Assimilation)**: 비음화, 유음화 (예: `국민` → `궁민`)

---

## API 레퍼런스 (API Reference)

### 핵심 함수

| 함수                     | 설명                        | 반환 타입 |
| :----------------------- | :-------------------------- | :-------- |
| `pronounce(text)`        | 텍스트를 표준 발음으로 변환 | `str`     |
| `pronounce_korean(text)` | `pronounce()`의 별칭        | `str`     |

### PronunciationEngine

고급 사용자를 위한 엔진 클래스:

```python
from pronunciation import PronunciationEngine

# 커스텀 엔진 생성
engine = PronunciationEngine()

# 발음 변환
result = engine.pronounce("한국어")
print(result)  # 한구거
```

### Rule Classes

각 음운 규칙은 독립적인 클래스로 구현되어 있습니다:

```python
from pronunciation.rules.effect import AspirationRule, PalatalizationRule
from pronunciation.rules.syllable import LiaisonRule, NeutralizationRule
from pronunciation.rules.assimilation import AssimilationRule

# 개별 규칙 사용 (고급)
aspiration = AspirationRule()
# ... (내부 API는 변경될 수 있습니다)
```

---

## 구현된 음운 규칙 (Implemented Rules)

### ✅ 완전 구현

| 규칙              | 설명                           | 예시                         |
| :---------------- | :----------------------------- | :--------------------------- |
| **음절말 중화**   | 종성 7개 대표음으로 단순화     | `옷` → `옫` (ㅅ→ㄷ)          |
| **자음군 단순화** | 겹받침 단순화 (문맥 의존)      | `값` → `갑`, `읽고` → `일꼬` |
| **연음**          | 종성이 다음 음절 초성으로 이동 | `밥이` → `바비`              |
| **ㅎ 탈락**       | 특정 환경에서 ㅎ 소실          | `싫어` → `시러`              |
| **격음화**        | ㅎ + 장애음 → 격음             | `놓고` → `노코`              |
| **구개음화**      | ㄷ/ㅌ + 이 → 지/치             | `같이` → `가치`              |
| **경음화**        | 장애음 뒤 평음 → 경음          | `국밥` → `국빱`              |
| **비음화**        | 장애음 + 비음 → 비음 + 비음    | `국민` → `궁민`              |
| **유음화**        | ㄴ + ㄹ / ㄹ + ㄴ → ㄹ + ㄹ    | `신라` → `실라`              |

### 🚧 향후 구현 예정

- **N-삽입**: `솜이불` → `솜니불`
- **사잇소리**: `나뭇가지` → `나문가지`
- **모음 조화**: `가아` → `가`
- **의 발음**: `민주주의의` → `민주주이에`

---

## 고급 사용 예제 (Advanced Usage)

### 배치 처리

```python
from pronunciation import pronounce

texts = [
    "안녕하세요",
    "반갑습니다",
    "좋은 하루 되세요"
]

results = [pronounce(text) for text in texts]
for original, pronounced in zip(texts, results):
    print(f"{original} → {pronounced}")
```

### 발음 비교 분석

```python
from pronunciation import pronounce

def analyze_pronunciation(word):
    """원문과 발음을 비교 분석"""
    pronunciation = pronounce(word)
    if word == pronunciation:
        print(f"✓ {word}: 발음 변화 없음")
    else:
        print(f"→ {word} → {pronunciation}")

        # 변화 분석
        if len(word) == len(pronunciation):
            for i, (o, p) in enumerate(zip(word, pronunciation)):
                if o != p:
                    print(f"  위치 {i+1}: '{o}' → '{p}'")

# 사용 예
analyze_pronunciation("국민")
# → 국민 → 궁민
#   위치 1: '국' → '궁'
```

---

## 성능 최적화 (Performance)

### 벤치마크

```python
from pronunciation import pronounce
import time

# 1만 단어 처리 벤치마크
words = ["한국어"] * 10000
start = time.time()
results = [pronounce(w) for w in words]
elapsed = time.time() - start

print(f"처리 시간: {elapsed:.3f}초")
print(f"처리 속도: {len(words)/elapsed:.0f} 단어/초")
# 일반적으로 10,000+ 단어/초 성능
```

---

## 트러블슈팅 (Troubleshooting)

### 자주 묻는 질문 (FAQ)

**Q: 일부 단어의 발음이 예상과 다릅니다.**
A: 현재 버전은 형태소 경계 정보 없이 작동하므로, 일부 경음화 규칙이 정확하지 않을 수 있습니다. 예: `신고` (신발을 신다 vs 신고하다)

**Q: 사잇소리 규칙이 적용되지 않습니다.**
A: 사잇소리 규칙은 v0.2.0에서 구현 예정입니다. 현재는 복합명사 분석이 필요한 규칙은 미구현 상태입니다.

**Q: 발음 변환 속도를 더 높일 수 있나요?**
A: 대량 처리 시 리스트 컴프리헨션을 사용하거나, 향후 Rust 포팅 버전을 사용하시면 됩니다.

---

## 기여 가이드 (Contributing)

새로운 음운 규칙을 추가하려면:

1. `pronunciation/src/pronunciation/rules/` 디렉토리에 새 규칙 클래스 생성
2. `PronunciationRule` 추상 클래스 상속
3. `apply()` 메서드 구현
4. `engine.py`의 파이프라인에 규칙 추가 (순서 주의!)

---

## 라이선스 (License)

본 모듈은 [MIT License](../../LICENSE)에 따라 배포됩니다.
공헌 및 버그 제보는 [GitHub Issues](https://github.com/jake1104/KULIM/issues)를 이용해 주시기 바랍니다.

---

<p align="center">
  Part of the KULIM Framework
</p>
