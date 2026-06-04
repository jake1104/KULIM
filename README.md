# KULIM (Korean Unified Linguistic Integration Manager)

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.2-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/rust-accelerated-orange.svg?style=flat-square&logo=rust" alt="Rust">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License">
</p>

<p align="center">
  <a href="README.en.md">English</a> | <b>한국어</b>
</p>

KULIM은 한국어 처리를 위한 통합 프레임워크로, 형태소 분석, 발음 변환, 로마자 표기 기능을 제공합니다.

## 패키지

| 패키지 | 버전 | 설명 |
|---------|---------|-------------|
| [grammar](grammar/) | 0.1.2 | 형태소 및 구문 분석 엔진 |
| [hangul](hangul/) | 0.1.2 | 한글 처리 유틸리티 (자모 분해/결합) |
| [pronunciation](pronunciation/) | 0.1.2 | 표준 발음 변환 |
| [romanization](romanization/) | 0.1.2 | 로마자 표기 (발음/철자 기반) |
| [kulim](kulim/) | 0.1.2 | 통합 라이브러리 인터페이스 |

## 빠른 시작

```bash
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
```

```python
from grammar import MorphAnalyzer
from pronunciation import pronounce
from romanization import romanize, romanize_standard

analyzer = MorphAnalyzer(use_rust=True)
result = analyzer.analyze("KULIM으로 한국어를 분석합니다.")
for m in result:
    print(f"{m.surface}/{m.pos}")

print(pronounce("값있는"))
print(romanize("읽고"))
print(romanize_standard("읽고"))
```

## 요구 사항

- Python 3.11+
- Rust toolchain (선택, 가속화된 trie 검색)
- CUDA 12.x (선택, GPU 가속 신경망 모델)

## 라이선스

MIT License. 학습 데이터셋(UD Korean Kaist)은 별도의 라이선스가 적용됩니다.

## 변경 내역

[CHANGELOG.md](CHANGELOG.md)를 참조하세요.
