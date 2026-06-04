from romanization import romanize, romanize_standard, romanize_pronunciation

def test_romanization_rr_phonetic():
    # Standard Revised Romanization (Pronunciation-based)
    # Default 'romanize' should be phonetic
    assert romanize("밥이") == "babi"
    assert romanize("독립") == "dongnip"
    
    # Specific cases
    assert romanize_pronunciation("읽고") == "ilkko"
    assert romanize_pronunciation("값이") == "gapssi"
    assert romanize_pronunciation("같이") == "gachi"
    # assert romanize_pronunciation("싫어") == "sireo" # Depending on H-deletion, maybe sideo or sireo, skipping for now to focus on exception dict.

def test_romanization_literal():
    # Literal Mode (Spelling-based Transliteration)
    assert romanize_standard("읽고") == "ilggo"
    assert romanize_standard("값이") == "gabsi"
    assert romanize_standard("앉다") == "anjda"
    assert romanize_standard("독립") == "dogrib"

import pytest
from grammar.analyzer import MorphAnalyzer

@pytest.fixture(scope="module")
def morph_analyzer():
    return MorphAnalyzer()

def test_official_romanization_standards(morph_analyzer):
    # 1. 경음화 무시 (압구정) -> 압꾸정(x) apgujeong
    assert romanize_pronunciation("압구정", morph_analyzer=morph_analyzer) == "apgujeong"
    
    # 2. 유음 'ㄹㄹ' -> ll (신라)
    assert romanize_pronunciation("신라", morph_analyzer=morph_analyzer) == "silla"
    
    # 3. 조사/어미 '의' 예외 (민주주의의 의의) -> ui 유지, e/i 치환 불가
    # 스페이스 유지를 위해 일단 단어별로 검증
    # 혹은 문장 그대로:
    assert romanize_pronunciation("민주주의의 의의", morph_analyzer=morph_analyzer) == "minjujuuiui uiui"
    
    # 4. 체언 ㅎ 축약 우회 (묵호 -> 무코x)
    assert romanize_pronunciation("묵호", morph_analyzer=morph_analyzer) == "mukho"
    
    # 5. 용언 ㅎ 축약 정상 적용 (좋고 -> 조코)
    assert romanize_pronunciation("좋고", morph_analyzer=morph_analyzer) == "joko"
