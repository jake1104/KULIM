# KULIM Romanization

<p align="center">
  <img src="https://img.shields.io/badge/package-romanization-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.1.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
</p>

---

## 개요 (Overview)

**KULIM Romanization**은 한글을 로마자로 변환하는 모듈로, 국립국어원의 **국어의 로마자 표기법**(Revised Romanization of Korean)을 기반으로 합니다.
발음 기반 표기와 철자 기반 표기, 두 가지 모드를 제공하여 다양한 사용 사례를 지원합니다.

### 주요 특징

- **Dual Modes**: 발음 기반(Phonetic) / 철자 기반(Literal) 두 가지 변환 모드
- **Standard Compliance**: 국립국어원 로마자 표기법 준수
- **Pronunciation Integration**: `pronunciation` 모듈과 통합하여 정확한 발음 기반 표기
- **Flexible Mapping**: 사용자 정의 매핑 테이블 지원

---

## 설치 가이드 (Installation)

```bash
# 독립 패키지로 설치
pip install romanization

# KULIM 통합 패키지에 포함되어 있습니다
pip install kulim
```

**의존성:**

- `hangul`: 자모 분해/결합 기능
- `pronunciation`: 발음 변환 기능 (발음 기반 모드에서 사용)

---

## 주요 기능 및 사용법 (Usage)

### 1. 발음 기반 로마자 표기 (Phonetic Mode)

표준 발음을 기준으로 로마자로 변환합니다.

```python
from romanization import romanize, romanize_pronunciation

# 기본 사용 (romanize는 romanize_pronunciation의 별칭)
print(romanize("한글"))           # hangeul
print(romanize("대한민국"))       # daehanminguk

# 발음 변화 반영
print(romanize("밥이"))           # babi (연음)
print(romanize("국민"))           # gungmin (비음화)
print(romanize("같이"))           # gachi (구개음화)
print(romanize("읽고"))           # ilkko (경음화)
print(romanize("놓고"))           # noko (격음화)

# 명시적 함수 사용
print(romanize_pronunciation("한국어"))  # hangugeo
```

### 2. 철자 기반 로마자 표기 (Literal Mode)

발음 변화 없이 철자를 그대로 로마자로 변환합니다.

```python
from romanization import romanize_standard

# 철자 기반 변환
print(romanize_standard("한글"))     # hangeul
print(romanize_standard("읽고"))     # ilggo (발음: ilkko)
print(romanize_standard("값이"))     # gabsi (발음: gapssi)
print(romanize_standard("앉다"))     # anjda (발음: antta)
print(romanize_standard("독립"))     # dogrib (발음: dongnip)

# 겹받침 처리
print(romanize_standard("닭"))       # dalg
print(romanize_standard("삶"))       # salm
```

### 3. 모드 비교

```python
from romanization import romanize, romanize_standard

words = ["읽고", "값이", "앉다", "국민", "같이"]

print("단어\t발음 기반\t철자 기반")
print("-" * 40)
for word in words:
    phonetic = romanize(word)
    literal = romanize_standard(word)
    print(f"{word}\t{phonetic}\t\t{literal}")

# 출력:
# 단어    발음 기반      철자 기반
# ----------------------------------------
# 읽고    ilkko          ilggo
# 값이    gapssi         gabsi
# 앉다    antta          anjda
# 국민    gungmin        gugmin
# 같이    gachi          gat-i
```

---

## 로마자 표기 규칙 (Romanization Rules)

### 자음 표기

#### 초성 (Initial Consonants)

| 한글 | 로마자 | 예시     |
| :--- | :----- | :------- |
| ㄱ   | g      | 가 → ga  |
| ㄲ   | kk     | 까 → kka |
| ㄴ   | n      | 나 → na  |
| ㄷ   | d      | 다 → da  |
| ㄸ   | tt     | 따 → tta |
| ㄹ   | r/l    | 라 → ra  |
| ㅁ   | m      | 마 → ma  |
| ㅂ   | b      | 바 → ba  |
| ㅃ   | pp     | 빠 → ppa |
| ㅅ   | s      | 사 → sa  |
| ㅆ   | ss     | 싸 → ssa |
| ㅇ   | (없음) | 아 → a   |
| ㅈ   | j      | 자 → ja  |
| ㅉ   | jj     | 짜 → jja |
| ㅊ   | ch     | 차 → cha |
| ㅋ   | k      | 카 → ka  |
| ㅌ   | t      | 타 → ta  |
| ㅍ   | p      | 파 → pa  |
| ㅎ   | h      | 하 → ha  |

#### 종성 (Final Consonants)

**발음 기반 (Phonetic):**

| 한글                       | 로마자 | 예시      |
| :------------------------- | :----- | :-------- |
| ㄱ, ㄲ, ㅋ, ㄳ, ㄺ         | k      | 국 → guk  |
| ㄴ, ㄵ, ㄶ                 | n      | 안 → an   |
| ㄷ, ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅎ | t      | 옷 → ot   |
| ㄹ, ㄼ, ㄽ, ㄾ, ㅀ         | l      | 말 → mal  |
| ㅁ, ㄻ                     | m      | 밤 → bam  |
| ㅂ, ㅄ, ㄿ                 | p      | 밥 → bap  |
| ㅇ                         | ng     | 강 → gang |

**철자 기반 (Literal):**

| 한글 | 로마자 | 예시            |
| :--- | :----- | :-------------- |
| ㄱ   | g      | 국 → gug        |
| ㄺ   | lg     | 읽 → ilg        |
| ㄻ   | lm     | 삶 → salm       |
| ㄼ   | lb     | 여덟 → yeodeolb |
| ㄳ   | gs     | 넋 → neogs      |
| ㅄ   | bs     | 값 → gabs       |

### 모음 표기

| 한글 | 로마자 | 예시     |
| :--- | :----- | :------- |
| ㅏ   | a      | 아 → a   |
| ㅐ   | ae     | 애 → ae  |
| ㅑ   | ya     | 야 → ya  |
| ㅒ   | yae    | 얘 → yae |
| ㅓ   | eo     | 어 → eo  |
| ㅔ   | e      | 에 → e   |
| ㅕ   | yeo    | 여 → yeo |
| ㅖ   | ye     | 예 → ye  |
| ㅗ   | o      | 오 → o   |
| ㅘ   | wa     | 와 → wa  |
| ㅙ   | wae    | 왜 → wae |
| ㅚ   | oe     | 외 → oe  |
| ㅛ   | yo     | 요 → yo  |
| ㅜ   | u      | 우 → u   |
| ㅝ   | wo     | 워 → wo  |
| ㅞ   | we     | 웨 → we  |
| ㅟ   | wi     | 위 → wi  |
| ㅠ   | yu     | 유 → yu  |
| ㅡ   | eu     | 으 → eu  |
| ㅢ   | ui     | 의 → ui  |
| ㅣ   | i      | 이 → i   |

---

## API 레퍼런스 (API Reference)

### 핵심 함수

| 함수                           | 설명                           | 모드     | 반환 타입 |
| :----------------------------- | :----------------------------- | :------- | :-------- |
| `romanize(text)`               | 발음 기반 로마자 표기 (기본)   | Phonetic | `str`     |
| `romanize_pronunciation(text)` | 발음 기반 로마자 표기 (명시적) | Phonetic | `str`     |
| `romanize_standard(text)`      | 철자 기반 로마자 표기          | Literal  | `str`     |
| `romanize_korean(text)`        | `romanize()`의 별칭            | Phonetic | `str`     |

### 매핑 테이블

내부 매핑 테이블에 접근할 수 있습니다:

```python
from romanization.romanization import CHO_MAP, JUNG_MAP, JONG_MAP, JONG_MAP_LITERAL

# 초성 매핑
print(CHO_MAP["ㄱ"])  # 'g'

# 중성 매핑
print(JUNG_MAP["ㅏ"])  # 'a'

# 종성 매핑 (발음 기반)
print(JONG_MAP["ㄱ"])  # 'k'

# 종성 매핑 (철자 기반)
print(JONG_MAP_LITERAL["ㄺ"])  # 'lg'
```

---

## 고급 사용 예제 (Advanced Usage)

### 배치 처리

```python
from romanization import romanize, romanize_standard

# 여러 단어 처리
words = ["서울", "부산", "대구", "인천", "광주"]
romanized = [romanize(w) for w in words]

for ko, en in zip(words, romanized):
    print(f"{ko} → {en}")

# 출력:
# 서울 → seoul
# 부산 → busan
# 대구 → daegu
# 인천 → incheon
# 광주 → gwangju
```

### 이름 로마자 표기

```python
from romanization import romanize

# 한국 이름 로마자 표기
names = ["김철수", "이영희", "박민수", "최지은"]
for name in names:
    print(f"{name} → {romanize(name).title()}")

# 출력:
# 김철수 → Gimcheolsu
# 이영희 → Iyeonghui
# 박민수 → Bangminsu
# 최지은 → Choejieun
```

### 주소 로마자 표기

```python
from romanization import romanize

address = "서울특별시 강남구 테헤란로"
print(romanize(address))
# seoulteukbyeolsi gangnamgu teheranro
```

---

## 사용 사례별 권장 모드 (Use Cases)

| 사용 사례          | 권장 모드             | 이유                    |
| :----------------- | :-------------------- | :---------------------- |
| 외국인 발음 가이드 | `romanize()`          | 실제 발음에 가까움      |
| 여권/공문서        | `romanize()`          | 표준 로마자 표기법 준수 |
| 데이터베이스 검색  | `romanize_standard()` | 철자 일관성             |
| 학술 논문          | `romanize()`          | 국제 표준               |
| 프로그래밍 변수명  | `romanize_standard()` | 예측 가능성             |

---

## 트러블슈팅 (Troubleshooting)

### 자주 묻는 질문 (FAQ)

**Q: 이름 표기 시 성과 이름 사이에 공백을 넣고 싶습니다.**
A: 입력 텍스트에 공백을 포함하세요: `romanize("김 철수")` → `"gim cheolsu"`

**Q: 대문자로 변환하려면 어떻게 하나요?**
A: Python의 문자열 메서드를 사용하세요:

```python
romanize("한국").upper()  # HANGUK
romanize("한국").title()  # Hanguk
```

**Q: 발음 기반과 철자 기반 중 어떤 것을 사용해야 하나요?**
A: 일반적으로 발음 기반(`romanize()`)을 권장합니다. 철자 기반은 데이터베이스 키나 프로그래밍 식별자처럼 일관성이 중요한 경우에 사용하세요.

**Q: 하이픈(-)은 언제 사용하나요?**
A: 현재 버전에서는 자동 하이픈 삽입을 지원하지 않습니다. 필요시 후처리로 추가하세요.

---

## 성능 최적화 (Performance)

```python
from romanization import romanize
import time

# 1만 단어 처리 벤치마크
words = ["한국어"] * 10000
start = time.time()
results = [romanize(w) for w in words]
elapsed = time.time() - start

print(f"처리 시간: {elapsed:.3f}초")
print(f"처리 속도: {len(words)/elapsed:.0f} 단어/초")
# 일반적으로 5,000+ 단어/초 성능
```

---

## 라이선스 (License)

본 모듈은 [MIT License](../../LICENSE)에 따라 배포됩니다.
공헌 및 버그 제보는 [GitHub Issues](https://github.com/jake1104/KULIM/issues)를 이용해 주시기 바랍니다.

---

<p align="center">
  Part of the KULIM Framework
</p>
