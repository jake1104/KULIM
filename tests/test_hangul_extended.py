import hangul

def test_old_hangul_recognition():
    # Old Hangul Characters
    # ᄀ (0x1100), ᅟ (0x115F), ᇹ (0x11F9) - Jamo
    assert hangul.is_hangul("\u1100")  # Choseong Kiyeok
    assert hangul.is_hangul("\uA960")  # Extended-A (Choseong Tikeut-Lieul)
    assert hangul.is_hangul("\uD7B0")  # Extended-B (Jongseong Nieun-Lieul)

def test_old_hangul_decompose():
    # Decompose should handle non-precomposed Jamos intelligently
    # For a standalone Choseong, it should return (char, '', '')
    
    # ᄀ (0x1100)
    cho, jung, jong = hangul.decompose("\u1100")
    assert cho == "\u1100"
    assert jung == ""
    assert jong == ""

    # Extended-A ꥠ (0xA960)
    cho, jung, jong = hangul.decompose("\uA960")
    assert cho == "\uA960"
    assert jung == ""
    assert jong == ""
    
    # Normal composed
    assert hangul.decompose("가") == ("ㄱ", "ㅏ", "")
