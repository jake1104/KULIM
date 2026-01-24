from typing import List
from .base import PronunciationRule, Phoneme

class AspirationRule(PronunciationRule):
    """격음화 (Aspiration)"""
    def apply(self, phonemes: List[Phoneme]) -> List[Phoneme]:
        for i, p in enumerate(phonemes):
            if not p.is_hangul or not p.jong: continue
            if i + 1 >= len(phonemes): continue
            
            nxt = phonemes[i+1]
            if not nxt.is_hangul: continue
            
            # Case 1: 받침 + ㅎ -> 격음
            if nxt.cho == 'ㅎ':
                merged = self._merge_h(p.jong)
                if merged:
                    nxt.cho = merged
                    # Remove the trigger part from jong
                    p.jong = self._remove_h_trigger(p.jong)
                    
            # Case 2: ㅎ(onset of jong) + ㄱ,ㄷ,ㅈ,ㅅ -> 격음 (+ㅅ->ㅆ)
            # ㅎ, ㄶ, ㅀ
            if p.jong in ['ㅎ', 'ㄶ', 'ㅀ']:
                if nxt.cho in ['ㄱ', 'ㄷ', 'ㅂ', 'ㅈ', 'ㅅ']:
                    if nxt.cho == 'ㄱ': nxt.cho = 'ㅋ'
                    elif nxt.cho == 'ㄷ': nxt.cho = 'ㅌ'
                    elif nxt.cho == 'ㅂ': nxt.cho = 'ㅍ'
                    elif nxt.cho == 'ㅈ': nxt.cho = 'ㅊ'
                    elif nxt.cho == 'ㅅ': nxt.cho = 'ㅆ'

                    # Simple logic: clear 'ㅎ' part from jong
                    if p.jong == 'ㅎ': p.jong = ''
                    elif p.jong == 'ㄶ': p.jong = 'ㄴ'
                    elif p.jong == 'ㅀ': p.jong = 'ㄹ'

        return phonemes

    def _merge_h(self, jong):
        # ㄳ cannot merge to ㅋ? 몫하다 -> [목카다]. Yes. ㄱ+ㅎ -> ㅋ.
        if any(c in jong for c in ['ㄱ', 'ㄲ', 'ㅋ']): return 'ㅋ'
        if any(c in jong for c in ['ㄷ', 'ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅌ']): return 'ㅌ'
        if any(c in jong for c in ['ㅂ', 'ㅍ']): return 'ㅍ'
        if any(c in jong for c in ['ㄵ', '앉']): return 'ㅊ' # 앉히다 -> 안치다
        return None

    def _remove_h_trigger(self, jong):
        # ㄺ + ㅎ -> ㄹ + ㅋ. Remove ㄱ.
        if jong == 'ㄺ': return 'ㄹ'
        if jong == 'ㄼ': return 'ㄹ'
        if jong == 'ㄵ': return 'ㄴ'
        if jong == 'ㄳ': return 'ㄴ' # (Correction from prev log: 몫하다 -> 목카다 means ㄳ->ㄱ then +ㅎ->ㅋ. residue is None?)
        # Just simplifies to '' for single jongs.
        if len(jong) == 1: return ''
        return '' # Simplify mostly

class PalatalizationRule(PronunciationRule):
    """구개음화 (Palatalization)"""
    def apply(self, phonemes: List[Phoneme]) -> List[Phoneme]:
        for i, p in enumerate(phonemes):
            if not p.is_hangul or not p.jong: continue
            if i + 1 >= len(phonemes): continue
            
            nxt = phonemes[i+1]
            if nxt.cho == 'ㅇ' and nxt.jung.startswith(('ㅣ', 'ㅑ', 'ㅕ', 'ㅛ', 'ㅠ')): 
                # Note: 'ㅖ' etc. handled loosely by startswith usually
                # Standard: 'ㄷ', 'ㅌ', 'ㄾ'
                if p.jong == 'ㄷ':
                    nxt.cho = 'ㅈ'; p.jong = ''
                elif p.jong == 'ㅌ':
                    nxt.cho = 'ㅊ'; p.jong = ''
                elif p.jong == 'ㄾ':
                    nxt.cho = 'ㅊ'; p.jong = 'ㄹ'
        return phonemes

class TensificationRule(PronunciationRule):
    """경음화 (Tensification)"""
    def apply(self, phonemes: List[Phoneme]) -> List[Phoneme]:
        TENS_MAP = {'ㄱ':'ㄲ', 'ㄷ':'ㄸ', 'ㅂ':'ㅃ', 'ㅅ':'ㅆ', 'ㅈ':'ㅉ'}
        
        for i, p in enumerate(phonemes):
            if not p.is_hangul or not p.jong: continue
            if i + 1 >= len(phonemes): continue
            
            nxt = phonemes[i+1]
            if nxt.cho not in TENS_MAP: continue
            
            # 1. Post-Obstruent (ㄱ,ㄷ,ㅂ)
            # Assuming Neutralization happened first!
            if p.jong in ['ㄱ', 'ㄷ', 'ㅂ']:
                nxt.cho = TENS_MAP[nxt.cho]
                
            # 2. Verb Stem Nasal/Liquid (ㄴ,ㅁ,ㄹ)
            # This requires 'original_jong' tracking from the Phoneme object.
            # 앉다 (orig: ㄵ) -> 안따
            if p.original_jong in ['ㄵ', 'ㄶ', 'ㄻ', 'ㄼ', 'ㄾ', 'ㅀ']:
                # Simplistic check: assumes this is a verb/adj if it has these clusters
                # (except numbers like 여덟?).
                nxt.cho = TENS_MAP[nxt.cho]
                
            # 3. Specific ㄺ (읽고 -> 일꼬)
            # ㄺ simplifies to 'ㄹ' before 'ㄱ'.
            if p.original_jong == 'ㄺ' and nxt.cho == 'ㄱ':
                 nxt.cho = 'ㄲ' # Already covered by simplified 'ㄱ' ? No.
                 # If simplified to 'ㄹ', then we need this rule.
                 
        return phonemes
