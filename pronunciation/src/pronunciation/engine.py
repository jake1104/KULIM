from typing import List
import hangul
from .rules.base import Phoneme, PronunciationRule
from .rules.syllable import NeutralizationRule, LiaisonRule
from .rules.effect import AspirationRule, PalatalizationRule, TensificationRule
from .rules.assimilation import AssimilationRule

class PronunciationEngine:
    """Core engine for Korean pronunciation."""
    
    def __init__(self):
        # Define the pipeline order.
        # Order is CRITICAL.
        # 1. Aspiration (ㅎ merge) & Palatalization & Liaison interaction
        # 2. Syllable Structure (Normalization)
        # 3. Tensification
        # 4. Assimilation
        
        self.pipeline: List[PronunciationRule] = [
            AspirationRule(),     # 격음화 (ㅎ + C -> C_tense) - should be early
            PalatalizationRule(), # 구개음화
            LiaisonRule(),        # 연음 & ㅎ 탈락
            NeutralizationRule(), # 음절 말 평파열음화 & 자음군 단순화
            TensificationRule(),  # 경음화
            AssimilationRule(),   # 동화 (비음화, 유음화)
        ]

    def pronounce(self, text: str) -> str:
        if not text: return ""

        # 1. Text -> Phonemes
        phonemes = self._text_to_phonemes(text)
        
        # 2. Apply Rules
        for rule in self.pipeline:
            phonemes = rule.apply(phonemes)
            
        # 3. Phonemes -> Text
        return "".join(p.compose() for p in phonemes)

    def _text_to_phonemes(self, text: str) -> List[Phoneme]:
        phonemes = []
        for char in text:
            if hangul.is_hangul(char):
                cho, jung, jong = hangul.decompose(char)
                p = Phoneme(
                    code=char,
                    cho=cho,
                    jung=jung,
                    jong=jong,
                    is_hangul=True,
                    original_jong=jong
                )
            else:
                p = Phoneme(
                    code=char,
                    cho='', jung='', jong='',
                    is_hangul=False
                )
            phonemes.append(p)
            
        # Link neighbors
        for i in range(len(phonemes)):
            if i > 0: phonemes[i].prev = phonemes[i-1]
            if i < len(phonemes) - 1: phonemes[i].next = phonemes[i+1]
            
        return phonemes
