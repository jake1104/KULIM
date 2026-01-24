from typing import List
from .base import PronunciationRule, Phoneme

class AssimilationRule(PronunciationRule):
    """자음 동화 (Assimilation: Nasalization, Liquidization)"""
    def apply(self, phonemes: List[Phoneme]) -> List[Phoneme]:
        # Assimilation can be iterative. e.g. 독립 -> [독닙] -> [동닙].
        # We run a loop until stable or fixed passes.
        
        changed = True
        limit = 3
        while changed and limit > 0:
            changed = False
            limit -= 1
            
            for i in range(len(phonemes) - 1):
                p = phonemes[i]
                nxt = phonemes[i+1]
                
                if not p.is_hangul or not nxt.is_hangul: continue
                if not p.jong: continue
                
                # 1. Liquidization (유음화)
                # ㄴ + ㄹ -> ㄹ + ㄹ
                if p.jong == 'ㄴ' and nxt.cho == 'ㄹ':
                    p.jong = 'ㄹ'; changed = True
                # ㄹ + ㄴ -> ㄹ + ㄹ
                elif p.jong == 'ㄹ' and nxt.cho == 'ㄴ':
                    nxt.cho = 'ㄹ'; changed = True
                    
                # 2. Nasalization of Liquids (Obstruent + ㄹ -> ... + ㄴ)
                # ㄱ,ㄷ,ㅂ,ㅁ,ㅇ + ㄹ -> ... + ㄴ
                if p.jong in ['ㄱ', 'ㄷ', 'ㅂ', 'ㅁ', 'ㅇ'] and nxt.cho == 'ㄹ':
                    nxt.cho = 'ㄴ'; changed = True
                    
                # 3. Nasalization of Obstruents (ㄱ,ㄷ,ㅂ + ㄴ,ㅁ -> ㅇ,ㄴ,ㅁ)
                if p.jong in ['ㄱ', 'ㄷ', 'ㅂ'] and nxt.cho in ['ㄴ', 'ㅁ']:
                    if p.jong == 'ㄱ': p.jong = 'ㅇ'; changed = True
                    elif p.jong == 'ㄷ': p.jong = 'ㄴ'; changed = True
                    elif p.jong == 'ㅂ': p.jong = 'ㅁ'; changed = True
                    
        return phonemes
