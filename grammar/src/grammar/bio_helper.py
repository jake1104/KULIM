from typing import List, Tuple


def convert_morphemes_to_bio(
    correct_morphemes: List[Tuple[str, str]],
) -> Tuple[List[str], List[str]]:
    """
    형태소 리스트를 (음절 리스트, BIO 태그 리스트)로 변환

    Args:
        correct_morphemes: [("오늘", "NNG"), ("은", "JX")]

    Returns:
        chars: ["오", "늘", "은"]
        tags: ["B-NNG", "I-NNG", "B-JX"]
    """
    chars = []
    tags = []

    for surf, pos in correct_morphemes:
        if not surf:
            continue

        # 첫 음절 B-POS
        chars.append(surf[0])
        tags.append(f"B-{pos}")

        # 나머지 음절 I-POS
        for c in surf[1:]:
            chars.append(c)
            tags.append(f"I-{pos}")

    return chars, tags
