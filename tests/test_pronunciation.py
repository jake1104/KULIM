from pronunciation import pronounce

def test_pronunciation_basic():
    # Basic Liaison
    assert pronounce("밥이") == "바비"
    assert pronounce("해돋이") == "해도지"

def test_pronunciation_complex_rules():
    # User requested cases
    assert pronounce("독립") == "동닙"       # Nasalization
    assert pronounce("값이") == "갑씨"       # Cluster simplification + Liaison
    assert pronounce("읽고") == "일꼬"       # Cluster simplification + Tensification
    assert pronounce("같이") == "가치"       # Palatalization
    assert pronounce("앉다") == "안따"       # Tensification
    assert pronounce("싫어") == "시러"       # H-deletion
    assert pronounce("놓고") == "노코"       # Aspiration
