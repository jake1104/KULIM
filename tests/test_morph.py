import pytest
from grammar import MorphAnalyzer


@pytest.fixture
def analyzer():
    return MorphAnalyzer(
        use_double_array=True,
        use_sejong=True,
        use_gpu=False,
        use_rust=False,
        debug=False,
    )


def test_morph_analysis_basic(analyzer):
    sent = "친구가 학교에 갔습니다."
    result = analyzer.analyze(sent)
    assert result is not None
    # Check if '친구' and '학교' are in the result
    morphemes = [m.surface for m in result]
    assert "친구" in morphemes
    assert "학교" in morphemes


@pytest.mark.parametrize(
    "sent",
    [
        "친구가 학교에 갔습니다.",
        "오늘 날씨가 좋네요!",
        "띄어쓰기가없네요",
        "컴퓨터로 프로그래밍을 공부합니다.",
    ],
)
def test_morph_analysis_sentences(analyzer, sent):
    result = analyzer.analyze(sent)
    assert result is not None
    assert len(result) > 0


def test_morph_analyzer_configs():
    # Test valid configurations initialization
    configs = [
        {"use_rust": False, "use_gpu": False},
        # Rust/GPU might not be available in all envs, so we just test init if possible
        # or we skip if not available, but MorphAnalyzer should handle it gracefully or we expect fallback
    ]

    for conf in configs:
        analyzer = MorphAnalyzer(
            use_double_array=True, use_sejong=True, debug=False, **conf
        )
        assert analyzer is not None
