from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Morph:
    """
    형태소 정보 클래스 (Morphological Information)
    """

    surface: str  # 표면형 (e.g. "갔")
    pos: str  # 품사 태그 (e.g. "VV")
    lemma: str  # 기본형 (e.g. "가다")
    score: float = 1.0  # 분석 점수/신뢰도
    start: int = 0  # 시작 위치 (문장 내)
    end: int = 0  # 끝 위치 (문장 내)

    # 복합 형태소 또는 활용 정보 (선택 사항)
    sub_morphs: List["Morph"] = field(default_factory=list)

    def __str__(self):
        if self.sub_morphs:
            return " + ".join([str(m) for m in self.sub_morphs])
        return f"{self.surface}/{self.pos}"

    def __repr__(self):
        return self.__str__()

    @property
    def is_composite(self) -> bool:
        """복합 형태소 여부"""
        return len(self.sub_morphs) > 0

    @property
    def is_lexical(self) -> bool:
        """
        실질형태소 여부 (Content Morpheme)
        구체적인 대상이나 상태를 나타내는 형태소 (명사, 동사/형용사 어근, 부사, 감탄사 등)
        """
        if self.pos.startswith("N"):  # 체언
            return True
        if self.pos.startswith("V") and self.pos not in [
            "VCP",
            "VCN",
        ]:  # 용언 (지정사 제외)
            return True
        if self.pos in ["VCP", "VCN"]:  # 지정사 어근 (이다/아니다) - 실질로 보기도 함
            return True
        if self.pos.startswith("M") or self.pos.startswith("I"):  # 수식언, 독립언
            return True
        if self.pos == "XR":  # 어근
            return True
        if self.pos in ["SL", "SH", "SN"]:  # 외국어, 한자, 숫자
            return True
        return False

    @property
    def is_functional(self) -> bool:
        """
        형식형태소 여부 (Functional/Grammatical Morpheme)
        문법적 관계를 나타내는 형태소 (조사, 어미, 접사)
        """
        if self.pos.startswith("J"):  # 관계언 (조사)
            return True
        if self.pos.startswith("E"):  # 어미
            return True
        if self.pos.startswith("X") and self.pos != "XR":  # 접사 (어근 제외)
            return True
        if self.pos.startswith("S"):  # 부호
            return True
        return False

    @property
    def is_free(self) -> bool:
        """
        자립형태소 여부 (Free Morpheme)
        혼자서 단어로 쓰일 수 있는 형태소 (명사, 대명사, 수사, 관형사, 부사, 감탄사)
        """
        if self.pos.startswith("N"):  # 체언
            return True
        if self.pos.startswith("M") or self.pos.startswith("I"):  # 수식언, 독립언
            return True
        if self.pos in ["SL", "SH", "SN"]:  # 외국어, 한자, 숫자
            return True
        return False

    @property
    def is_bound(self) -> bool:
        """
        의존형태소 여부 (Bound Morpheme)
        혼자 쓰일 수 없고 다른 형태소와 결합해야 하는 형태소 (조사, 용언 어근, 어미, 접사)
        """
        if self.pos.startswith("V"):  # 용언 어간은 의존적임
            return True
        if self.pos.startswith("J"):  # 조사
            return True
        if self.pos.startswith("E"):  # 어미
            return True
        if self.pos.startswith("X"):  # 접사, 어근
            return True
        if self.pos.startswith("S"):  # 부호
            return True
        return False


def is_lexical_morph(morph: Morph) -> bool:
    """실질형태소 여부 판별 함수"""
    return morph.is_lexical


def is_functional_morph(morph: Morph) -> bool:
    """형식형태소 여부 판별 함수"""
    return morph.is_functional


def is_free_morph(morph: Morph) -> bool:
    """자립형태소 여부 판별 함수"""
    return morph.is_free


def is_bound_morph(morph: Morph) -> bool:
    """의존형태소 여부 판별 함수"""
    return morph.is_bound
