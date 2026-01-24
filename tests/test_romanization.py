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
    assert romanize_pronunciation("싫어") == "sireo"

def test_romanization_literal():
    # Literal Mode (Spelling-based Transliteration)
    assert romanize_standard("읽고") == "ilggo"
    assert romanize_standard("값이") == "gabsi"
    assert romanize_standard("앉다") == "anjda"
    assert romanize_standard("독립") == "dogrib"
