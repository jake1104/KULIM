from grammar import Morph, is_lexical_morph, is_free_morph


def test_morph_classification():
    # 1. 실질형태소 / 자립형태소 (명사)
    m1 = Morph(surface="학교", pos="NNG", lemma="학교")
    print(f"[{m1}] 실질: {m1.is_lexical}, 자립: {m1.is_free}")
    assert m1.is_lexical == True
    assert m1.is_free == True

    # 2. 실질형태소 / 의존형태소 (동사 어간)
    m2 = Morph(surface="가", pos="VV", lemma="가다")
    print(f"[{m2}] 실질: {m2.is_lexical}, 자립: {m2.is_free}")
    assert m2.is_lexical == True
    assert m2.is_free == False

    # 3. 형식형태소 / 의존형태소 (조사)
    m3 = Morph(surface="가", pos="JKS", lemma="가")
    print(f"[{m3}] 형식: {m3.is_functional}, 의존: {m3.is_bound}")
    assert m3.is_functional == True
    assert m3.is_bound == True

    # 4. 형식형태소 / 의존형태소 (어미)
    m4 = Morph(surface="았", pos="EP", lemma="았")
    print(f"[{m4}] 형식: {m4.is_functional}, 의존: {m4.is_bound}")
    assert m4.is_functional == True
    assert m4.is_bound == True

    # Standalone function check
    assert is_lexical_morph(m1) == True
    assert is_free_morph(m2) == False

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_morph_classification()
