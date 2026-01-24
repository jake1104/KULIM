# KULIM (Korean Unified Linguistic Integration Manager)

<p align="center">
  <a href="README.en.md">English</a> | <b>한국어</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.1-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/rust-accelerated-orange.svg?style=flat-square&logo=rust" alt="Rust">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/status-experimental-red.svg?style=flat-square" alt="Status">
</p>

---

**KULIM**은 현대적인 한국어 처리를 위해 설계된 고성능 언어 처리 프레임워크입니다.
단순히 텍스트를 분석하는 것을 넘어, 한글 자모 처리부터 딥러닝 기반의 정밀 구문 분석까지 아우르는 **통합 솔루션**을 지향합니다.

Python의 생산성과 Rust의 저수준 성능을 결합하여, 대규모 데이터 처리부터 복잡한 언어학적 연구까지 폭넓은 스펙트럼의 요구사항을 충족합니다.

## 핵심 기능

- **하이브리드 엔진**: 사전 기반의 정확성과 Transformer 기반의 유연성을 결합한 형태소 분석.
- **초고속 성능**: 핵심 알고리즘을 Rust로 재작성하여 기존 Python 엔진 대비 비약적인 처리 속도 향상.
- **정밀 구문 분석**: Universal Dependencies 표준을 따르는 의존 구문 분석 및 문장 성분 판별.
- **확장성**: GPU 가속 지원 및 온라인 학습(Online Learning) API를 통한 실시간 모델 업데이트.

## 프로젝트 로드맵 (Package Roadmap)

1.  **[grammar](grammar/)**: 핵심 언어 분석 엔진 (형태소, 구문 분석)
2.  **[hangul](hangul/)**: 기초 한글 처리 유틸리티 (자모 분해, 결합, 옛한글 지원)
3.  **[pronunciation](pronunciation/)**: 고성능 표준 발음 변환 엔진 (파이프라인 아키텍처)
4.  **[romanization](romanization/)**: 국어의 로마자 표기법 변환 (발음 기반/철자 기반 모드)
5.  **[kulim](kulim/)**: 통합 라이브러리 인터페이스

## 시작하기 (Quick Start)

KULIM은 현대적인 패키지 매니저인 `uv` 사용을 권장합니다.

```bash
# 저장소 복제 및 환경 설정
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
```

### 기본 사용법

```python
from grammar import MorphAnalyzer
from pronunciation import pronounce
from romanization import romanize, romanize_standard

# 1. 형태소 분석
analyzer = MorphAnalyzer(use_rust=True)
result = analyzer.analyze("KULIM으로 한국어를 분석합니다.")
for m in result:
    print(f"{m.surface}/{m.pos}")

# 2. 표준 발음 변환
print(pronounce("값있는"))  # -> [가빈는]

# 3. 로마자 표기 (두 가지 모드)
print(romanize("읽고"))           # -> ilkko (표준 발음 기반)
print(romanize_standard("읽고"))  # -> ilggo (철자 기반 단순 변환)
```

## 프로젝트 상태 및 법적 고지 (Project Status & Disclaimer)

본 버전(`v0.1.1`)은 KULIM의 첫 번째 공식 릴리즈이지만, 여전히 알고리즘 고도화와 데이터 구조 최적화가 진행 중인 **실험적 버전(Experimental Release)**으로 간주됩니다.

> [!WARNING]
>
> - **Zero Warranty**: 본 소프트웨어는 '있는 그대로' 제공되며, 분석 결과의 정확성이나 이로 인해 발생한 유무형의 손실에 대해 저작권자는 법적 책임을 지지 않습니다.
> - **Breaking Changes**: v1.0.0 정식 버전 도달 전까지 API 명세가 예고 없이 변경될 수 있습니다.
> - **Production Note**: 실서비스 환경에 도입 전 반드시 충분한 검증 과정을 거치시기 바랍니다.

## 변경 이력 (Changelog)

자세한 버전별 변경 사항은 [CHANGELOG.md](CHANGELOG.md)에서 확인하실 수 있습니다.

## 피드백 및 기여 (Feedback & Contribution)

KULIM은 오픈 소스 프로젝트로 여러분의 기여를 환영합니다.

- **Issues**: 버그 보고 및 기능 제안은 [GitHub Issues](https://github.com/jake1104/KULIM/issues)를 이용해 주세요.
- **Contact**: 기술 문의 및 협업 제안은 [iamjake1104@gmail.com](mailto:iamjake1104@gmail.com)으로 연락 바랍니다.

## 라이선스 (License)

본 프로젝트는 **MIT License**를 따릅니다.
단, 학습에 사용된 데이터셋([UD Korean Kaist](https://universaldependencies.org/treebanks/ko_kaist/index.html))의 라이선스 규정을 함께 확인하시기 바랍니다.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jake1104">jake1104</a>
</p>
