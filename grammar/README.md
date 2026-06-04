# KULIM Grammar

<p align="center">
  <img src="https://img.shields.io/badge/package-grammar-blue.svg?style=flat-square" alt="Package">
  <img src="https://img.shields.io/badge/version-v0.1.3-blue.svg?style=flat-square" alt="Version">
  <a href="README.en.md"><img src="https://img.shields.io/badge/lang-english-green.svg?style=flat-square" alt="English"></a>
</p>

한국어 형태소 분석 및 의존 구문 분석 엔진.

## 기능

- Viterbi 기반 형태소 분석 (사전 검색 + 활용 복원)
- Transformer 기반 신경망 형태소 태거 (선택, 경량)
- Biaffine Attention 기반 의존 구문 분석 (선택)
- `train()` API를 통한 온라인 학습
- Rust 가속 trie 검색 (선택)
- CoNLL-U 형식 학습 및 HMM 전이/방출 확률 추정
- 27개 POS 태그 (세종 태그셋 기반) 및 50+ 전이 제약

## 설치

```bash
pip install kulim
```

## CLI

```bash
# 텍스트 분석
uv run grammar analyze "오늘 날씨가 좋네요."

# CoNLL-U 코퍼스로 학습
uv run grammar train data/train.conllu --epochs 10

# .kg 패키지로 저장
uv run grammar save --output model.kg

# 대화형 분석
uv run grammar analyze --interactive
```

## API

```python
from grammar import MorphAnalyzer, SyntaxAnalyzer

analyzer = MorphAnalyzer()
result = analyzer.analyze("한국어를 분석합니다.")
for m in result:
    print(f"{m.surface}/{m.pos}")

syntax = SyntaxAnalyzer()
components = syntax.analyze("한국어를 분석합니다.", analyzer)
```

### MorphAnalyzer

| 메서드 | 설명 |
|--------|------|
| `analyze(text)` | `Morph` 객체 리스트 반환 |
| `train(sentence, morphs)` | 온라인 학습 |
| `save()` | 사전 영구 저장 |
| `save_model(path)` | .kg 파일로 모델 패키징 |
| `load_model(path)` | .kg 파일에서 모델 로드 |

### 학습

```bash
# CoNLL-U로 HMM 학습
uv run grammar train corpus/ko_kaist.conllu

# 신경망 태거 학습
uv run grammar train corpus/ --neural --epochs 10 --batch-size 64

# 대화형 모드 (단일 문장 추가)
uv run grammar train --interactive
```

학습 데이터 형식 (단순):
```
친구/NNG + 가/JKS + 학교/NNG + 에/JKB + 가/VV + 었/EP + 다/EF + ./SF
```

### POS 태그셋 (세종 기반)

| 태그 | 품사 | 예시 |
|------|------|------|
| NNG | 일반명사 | 사람, 나라, 책 |
| NNP | 고유명사 | 서울, 한국 |
| NNB | 의존명사 | 것, 수, 데 |
| NP | 대명사 | 나, 저, 너 |
| NR | 수사 | 하나, 둘, 셋 |
| VV | 동사 | 가다, 먹다, 보다 |
| VA | 형용사 | 좋다, 크다, 예쁘다 |
| VX | 보조용언 | 있다, 싶다, 않다 |
| VCP | 긍정지정사 | 이다 |
| VCN | 부정지정사 | 아니다 |
| MM | 관형사 | 이, 그, 저 |
| MAG | 일반부사 | 매우, 아주, 정말 |
| IC | 감탄사 | 네, 아니요 |
| JKS | 주격조사 | 이, 가 |
| JKO | 목적격조사 | 을, 를 |
| JKG | 관형격조사 | 의 |
| JKB | 부사격조사 | 에, 에서, 로 |
| JKV | 호격조사 | 아, 야 |
| JC | 접속조사 | 와, 과, 하고 |
| JX | 보조사 | 은, 는, 도, 만 |
| EP | 선어말어미 | 시, 었, 겠 |
| EF | 종결어미 | 다, 요, 까 |
| EC | 연결어미 | 고, 면, 서 |
| ETM | 관형형전성어미 | ㄴ, 는, ㄹ |
| ETN | 명사형전성어미 | 기, ㅁ, 음 |
| XPN | 접두사 | 맨, 늦, 짓 |
| XSN | 명사파생접미사 | 음, 개, 이 |
| XSV | 동사파생접미사 | 하, 되, 시키 |
| XSA | 형용사파생접미사 | 답, 롭, 스럽 |
| SF | 마침표/물음표/느낌표 | ., ?, ! |
| SP | 기타 구두점 | , |

## 라이선스

MIT. [LICENSE](../../LICENSE) 참조.
