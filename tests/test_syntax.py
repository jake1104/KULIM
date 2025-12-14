import pytest
from grammar import SyntaxAnalyzer, MorphAnalyzer, SentenceComponent


@pytest.fixture
def morph_analyzer():
    return MorphAnalyzer(use_double_array=True, use_sejong=True, debug=False)


@pytest.fixture
def syntax_analyzer():
    return SyntaxAnalyzer()


@pytest.mark.parametrize(
    "sent, expected_keywords",
    [
        ("친구가 학교에 갔습니다.", ["친구", "학교"]),
        ("나는 밥을 먹었다.", ["나", "밥"]),
        ("철수가 의사가 되었습니다.", ["철수", "의사"]),
    ],
)
def test_syntax_analysis(syntax_analyzer, morph_analyzer, sent, expected_keywords):
    components = syntax_analyzer.analyze(text=sent, morph_analyzer=morph_analyzer)
    assert components is not None
    assert len(components) > 0

    words = [item[0] for item in components]
    for key in expected_keywords:
        assert any(key in w for w in words)


def test_syntax_component_types(syntax_analyzer, morph_analyzer):
    sent = "철수가 의사가 되었습니다."  # '의사가' should be close to Complement (보어)
    components = syntax_analyzer.analyze(text=sent, morph_analyzer=morph_analyzer)

    # Check if we have SentenceComponent enum values
    assert any(isinstance(c[2], SentenceComponent) for c in components)
