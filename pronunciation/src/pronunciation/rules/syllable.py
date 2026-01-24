from typing import List
import hangul
from .base import PronunciationRule, Phoneme

class NeutralizationRule(PronunciationRule):
    """음절 말 평파열음화 (Syllable Coda Neutralization)"""
    
    JONG_NEUTRAL = {
        "ㄲ": "ㄱ", "ㄳ": "ㄱ", "ㅋ": "ㄱ",
        "ㅅ": "ㄷ", "ㅆ": "ㄷ", "ㅈ": "ㄷ", "ㅊ": "ㄷ", "ㅌ": "ㄷ", "ㅎ": "ㄷ",
        "ㄼ": "ㄹ", "ㄽ": "ㄹ", "ㄾ": "ㄹ", "ㅀ": "ㄹ",
        "ㄵ": "ㄴ", "ㄶ": "ㄴ",
        "ㄻ": "ㅁ",
        "ㄿ": "ㅂ", "ㅄ": "ㅂ",
    }
    
    # Context-sensitive simplification (어말 또는 자음 앞)
    CLUSTER_SIMPLE = {
        "ㄳ": "ㄱ", "ㄵ": "ㄴ", "ㄶ": "ㄴ", "ㄺ": "ㄱ", "ㄻ": "ㅁ",
        "ㄼ": "ㄹ", "ㄽ": "ㄹ", "ㄾ": "ㄹ", "ㄿ": "ㅂ", "ㅀ": "ㄹ", "ㅄ": "ㅂ"
    }

    def apply(self, phonemes: List[Phoneme]) -> List[Phoneme]:
        for i, p in enumerate(phonemes):
            if not p.is_hangul or not p.jong:
                continue
            
            # Check if followed by Vowel (Liaison handles this, so we skip if next is vowel)
            # EXCEPT if the next char is NOT a hangul/null but actually a vowel? 
            # In standard Korean, empty onset 'ㅇ' + vowel is the condition.
            # However, LiaisonRule should run BEFORE Neutralization.
            # If Liaison ran, the jong would be moved or empty.
            # So here we just simplify whatever is left.
            
            # Special check: If next is 'ㅇ', we usually don't neutralize unless it's a specific boundary
            # but standard rule is Liaison first. 
            # Assuming LiaisonRule implies we only have 'neutralizable' codas left.
            
            # Check Simplification (reading `ㄺ` as `ㄹ` or `ㄱ`?)
            # 읽고 [일꼬] (next is ㄱ)
            next_cho = phonemes[i+1].cho if (i+1 < len(phonemes) and phonemes[i+1].is_hangul) else ''
            
            simplified = self._simplify(p.jong, next_cho)
            neutralized = self.JONG_NEUTRAL.get(simplified, simplified)
            
            p.jong = neutralized
            
        return phonemes

    def _simplify(self, jong: str, next_cho: str) -> str:
        if jong == 'ㄺ' and next_cho == 'ㄱ':
            return 'ㄹ'
        return self.CLUSTER_SIMPLE.get(jong, jong)


class LiaisonRule(PronunciationRule):
    """연음 법칙 (Liaison)"""
    
    def apply(self, phonemes: List[Phoneme]) -> List[Phoneme]:
        for i, p in enumerate(phonemes):
            if not p.is_hangul or not p.jong:
                continue
                
            if i + 1 >= len(phonemes):
                continue
                
            nxt = phonemes[i+1]
            if not nxt.is_hangul:
                continue
                
            # If next starts with vowel (cho == 'ㅇ')
            if nxt.cho == 'ㅇ':
                # H-deletion check typically happens here or before.
                # ㅎ, ㄶ, ㅀ + Vowel
                if p.jong in ['ㅎ', 'ㄶ', 'ㅀ']:
                    # ㅎ drops
                    if p.jong == 'ㅎ': 
                        p.jong = ''
                    elif p.jong == 'ㄶ': 
                        p.jong = 'ㄴ'
                        # ㄴ moves to next
                        nxt.cho = 'ㄴ'; p.jong = ''
                    elif p.jong == 'ㅀ': 
                        p.jong = 'ㄹ'
                        # ㄹ moves to next
                        nxt.cho = 'ㄹ'; p.jong = ''
                    continue

                # Standard Liaison
                # 홑받침
                if p.jong in hangul.CHOSUNG:
                    nxt.cho = p.jong
                    p.jong = ''
                # 겹받침
                else:
                    front, back = self._split_cluster(p.jong)
                    if back:
                        p.jong = front
                        nxt.cho = back # 넋이 -> 넉시
                        if back == 'ㅅ': nxt.cho = 'ㅆ' # 값이 -> 갑씨
                        
        return phonemes

    def _split_cluster(self, jong: str) -> tuple:
        # Maps complex coda to (residue, moved)
        # ㄳ -> ㄱ, ㅅ
        if jong == 'ㄳ': return 'ㄱ', 'ㅅ'
        if jong == 'ㄵ': return 'ㄴ', 'ㅈ'
        if jong == 'ㄶ': return 'ㄴ', 'ㅎ' # Should be handled by H-del but distinct rule?
        if jong == 'ㄺ': return 'ㄹ', 'ㄱ'
        if jong == 'ㄻ': return 'ㄹ', 'ㅁ'
        if jong == 'ㄼ': return 'ㄹ', 'ㅂ'
        if jong == 'ㄽ': return 'ㄹ', 'ㅅ'
        if jong == 'ㄾ': return 'ㄹ', 'ㅌ'
        if jong == 'ㄿ': return 'ㄹ', 'ㅍ'
        if jong == 'ㅀ': return 'ㄹ', 'ㅎ'
        if jong == 'ㅄ': return 'ㅂ', 'ㅅ'
        return jong, ''
