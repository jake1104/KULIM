# KULIM v0.1.1 Release Notes

## 🎉 첫 번째 공식 릴리스

KULIM (Korean Unified Linguistic Integration Manager) v0.1.1을 공개합니다!

### ✨ 주요 기능

#### 📦 패키지 구성

1. **grammar (v0.1.1)** - 핵심 형태소 분석 엔진
   - Hybrid 분석: Viterbi + Transformer
   - Rust 가속 Trie 자료구조
   - GPU 지원
   - **NEW**: `.kg` 모델 패키징 포맷

2. **hangul (v0.1.0)** - 한글 처리 유틸리티
   - 자모 분해/결합
   - 옛한글 지원 (Extended Jamo)

3. **pronunciation (v0.1.0)** - 표준 발음 변환
   - 파이프라인 아키텍처
   - 9가지 음운 규칙 구현

4. **romanization (v0.1.0)** - 로마자 표기
   - 발음 기반 / 철자 기반 이중 모드

5. **kulim** - 통합 인터페이스

### 🚀 Grammar v0.1.1 신기능

- **모델 패키징**: 6개 파일 → 1개 `.kg` 파일로 통합
- **CLI 명령어**: `uv run grammar save --output <path>`
- **Python API**: `analyzer.save_model()` / `MorphAnalyzer.load_model()`
- **모델 경로 지정**: `MorphAnalyzer(model_path="model.kg")`

### 📚 문서

- 한글/영문 README 완비
- 모든 모듈별 상세 문서
- API 레퍼런스
- 사용 예제

### 🔧 설치

```bash
git clone https://github.com/jake1104/KULIM.git
cd KULIM
uv sync --all-extras
```

### 💡 사용 예제

```python
from grammar import MorphAnalyzer
from pronunciation import pronounce
from romanization import romanize

# 형태소 분석
analyzer = MorphAnalyzer(use_rust=True)
result = analyzer.analyze("한국어를 분석합니다")

# 발음 변환
print(pronounce("값있는"))  # 가빈는

# 로마자 표기
print(romanize("읽고"))  # ilkko
```

### ⚠️ 주의사항

- 실험적 정식 버전 (Experimental Release)
- API 변경 가능성 있음 (v1.0.0 이전)
- 프로덕션 사용 시 충분한 검증 필요

### 🙏 감사의 말

이 프로젝트는 UD Korean Kaist 데이터셋을 사용합니다.

---

**Full Changelog**: https://github.com/jake1104/KULIM/blob/main/CHANGELOG.md
