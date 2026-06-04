from typing import List, Tuple, Optional, Dict
import hangul

# 음절 말 평파열음화 (Neutralization)
JONG_NEUTRAL = {
    "ㄲ": "ㄱ", "ㄳ": "ㄱ", "ㅋ": "ㄱ",
    "ㅅ": "ㄷ", "ㅆ": "ㄷ", "ㅈ": "ㄷ", "ㅊ": "ㄷ", "ㅌ": "ㄷ", "ㅎ": "ㄷ",
    "ㅍ": "ㅂ",
    "ㄼ": "ㄹ", "ㄽ": "ㄹ", "ㄾ": "ㄹ", "ㅀ": "ㄹ",
    "ㄵ": "ㄴ", "ㄶ": "ㄴ",
    "ㄻ": "ㅁ",
    "ㄿ": "ㅂ", "ㅄ": "ㅂ",
}

# 겹받침 단순화 (Cluster Simplification) - 어말/자음 앞
CLUSTER_SIMPLE = {
    "ㄳ": "ㄱ", "ㄵ": "ㄴ", "ㄶ": "ㄴ", "ㄺ": "ㄱ", "ㄻ": "ㅁ",
    "ㄼ": "ㄹ", "ㄽ": "ㄹ", "ㄾ": "ㄹ", "ㄿ": "ㅂ", "ㅀ": "ㄹ", "ㅄ": "ㅂ"
}

def simplify_cluster(jong: str, next_cho: str = '') -> str:
    # ㄺ 예외: 'ㄱ' 앞에서는 'ㄹ'로 발음 (읽고 -> 일꼬)
    if jong == 'ㄺ' and next_cho == 'ㄱ':
        return 'ㄹ'
    if jong == 'ㄼ': # 밟다 -> 밥따 (예외 - 단어 단위 확인 필요하나 여기선 불가)
        return 'ㄹ' # 일반적으론 ㄹ
    if jong == '넓' and next_cho in ['ㅈ','ㅅ']: # 넓죽하다 등. (Hard to catch without word info)
        pass 
        
    return CLUSTER_SIMPLE.get(jong, jong)

def pronounce(text: str, morph_analyzer=None, is_romanization=False) -> str:
    """한글 문장을 표준 발음으로 변환합니다."""
    if not text:
        return ""

    # =========================================================================
    # 0. Exception Dictionary & POS-based Context (Pre-processing)
    # =========================================================================
    # Hardcoded or explicit exception dictionary for words that don't follow standard rules
    # or have idiomatic pronunciations.
    OVI_DICTIONARY = {
        "깻잎": "깬닙",
        "순대국": "순대꾹",
        "효과": "효꽈",
        "불법": "불뻡",
        "관건": "관껀",
        "인사말": "인사말", # (not 인산말)
        "머리말": "머리말",
    }
    
    char_pos_map: Dict[int, str] = {}
    
    # If a MorphAnalyzer is provided, we can leverage POS tags for precise pronunciation.
    if morph_analyzer:
        # Example: '의' pronunciation rules
        # 1. First syllable of a word -> [의] (의사 -> 의사)
        # 2. Not first syllable -> [이] permitted, standard is [의]. (우리의 -> [우리에], 민주주의 -> [민주주의/민주주이])
        # 3. JKG (Genitive particle '의') -> [에]
        
        morphemes = morph_analyzer.analyze(text)
        if morphemes:
            # Reconstruct text with POS-aware surface changes if needed
            refined_text = ""
            char_idx = 0
            text_idx = 0
            for i, m in enumerate(morphemes):
                surface = m.surface
                pos = m.pos
                
                # Check Exception Dict first for the whole surface
                if surface in OVI_DICTIONARY:
                    surface = OVI_DICTIONARY[surface]
                else:
                    # POS Specific Rules
                    if pos == "JKG" and surface == "의":
                        # 로마자 표기 시에는 '의'를 그대로 유지
                        if not is_romanization:
                            surface = "에" # Genitive particle is pronounced '에'
                
                # find where this morpheme starts in text to preserve spaces
                idx = text.find(m.surface, text_idx)
                if idx != -1:
                    # append the spaces or punctuations that were skipped
                    skipped = text[text_idx:idx]
                    refined_text += skipped
                    for _ in range(len(skipped)):
                        char_pos_map[char_idx] = "SP" # mark space/punct
                        char_idx += 1
                        
                    text_idx = idx + len(m.surface)
                
                refined_text += surface
                for _ in range(len(surface)):
                    char_pos_map[char_idx] = pos
                    char_idx += 1
            
            # append any trailing characters
            if text_idx < len(text):
                trailing = text[text_idx:]
                refined_text += trailing
                for _ in range(len(trailing)):
                    char_pos_map[char_idx] = "SP"
                    char_idx += 1
                    
            text = refined_text
    else:
        # Without POS, apply simple Exception Dictionary search & replace.
        for keyword, pron in OVI_DICTIONARY.items():
            text = text.replace(keyword, pron)

    chars = []
    # Track original jongsung for Tensification rules (e.g. ㄵ -> ㄴ but triggers tensification)
    original_jongs: Dict[int, str] = {}
    
    for i, char in enumerate(text):
        if hangul.is_hangul(char):
            decomp = list(hangul.decompose(char))
            chars.append(decomp)
            original_jongs[i] = decomp[2] # Store original jong
        else:
            chars.append(char)

    n = len(chars)

    # =========================================================================
    # 1. 형태소 경계/음운 변동 전처리 (Aspiration, Palatalization, Liaison)
    #    순서: 구개음화 -> 격음화 -> 연음 -> ㅎ탈락
    # =========================================================================
    
    # [Pass 1] Aspiration (격음화) & H-Interaction
    i = 0
    while i < n - 1:
        curr = chars[i]; nxt = chars[i+1]
        if not isinstance(curr, list) or not isinstance(nxt, list):
            i+=1; continue
        
        jong1 = curr[2]
        cho2 = nxt[0]
        
        merged_cho = None
        
        # Case A: 받침 + ㅎ
        if cho2 == 'ㅎ':
            # 체언의 'ㄱ,ㄷ,ㅂ' 연속 ㅎ 격음화 예외 (로마자 표기용)
            if is_romanization and jong1 in ['ㄱ', 'ㄷ', 'ㅂ']:
                pos_curr = char_pos_map.get(i, "")
                pos_next = char_pos_map.get(i+1, "")
                if pos_curr.startswith("N") or pos_next.startswith("N"):
                    i += 1
                    continue

            if jong1 in ['ㄱ', 'ㄲ', 'ㅋ', 'ㄳ', 'ㄺ']: merged_cho = 'ㅋ'
            elif jong1 in ['ㄷ', 'ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅌ']: merged_cho = 'ㅌ'
            elif jong1 in ['ㅂ', 'ㅍ', 'ㄼ', 'ㄿ', 'ㅄ']: merged_cho = 'ㅍ'
            elif jong1 in ['ㅈ', 'ㄵ']: merged_cho = 'ㅊ'
            
            # ㅎ 그 자체 (좋고 -> 조코)
            elif jong1 in ['ㅎ', 'ㄶ', 'ㅀ']:
                 # ㄶ, ㅀ followed by ㅎ (많효? rare)
                 # Usually ㅎ+ㅎ doesn't happen strictly within morph boundary logic here.
                 # But '좋흐..' -> 조트? No.
                 pass

            if merged_cho:
                chars[i+1][0] = merged_cho
                # 종성 정리 (Complex cluster handling)
                if jong1 in ['ㄺ', 'ㄼ', 'ㄵ', 'ㄳ', 'ㄶ', 'ㅀ', 'ㄻ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅄ']:
                    # Remove the h-merging part from cluster?
                    # ㄺ+ㅎ -> ㄹㅋ. So jong becomes ㄹ.
                    if jong1 == 'ㄺ': chars[i][2] = 'ㄹ'
                    elif jong1 == 'ㄼ': chars[i][2] = 'ㄹ'
                    elif jong1 == 'ㄵ': chars[i][2] = 'ㄴ'
                    elif jong1 == 'ㄳ': chars[i][2] = '' # 몫하다 -> [목카다], ㅅ 탈락
                    # Let's simplify: map to primary residue
                    elif jong1 == 'ㄶ': chars[i][2] = 'ㄴ'
                    elif jong1 == 'ㅀ': chars[i][2] = 'ㄹ'
                    else: chars[i][2] = '' # standard single jong removal
                else: 
                     chars[i][2] = '' # single jong removed

        # Case B: ㅎ(겹받침 포함) + 평음 (놓고 -> 노코, 닳고 -> 달코)
        if jong1 in ['ㅎ', 'ㄶ', 'ㅀ']:
             if cho2 in ['ㄱ', 'ㄷ', 'ㅂ', 'ㅈ', 'ㅅ']:
                 if jong1 == 'ㅎ':
                     if cho2 == 'ㄱ': chars[i+1][0] = 'ㅋ'; chars[i][2] = ''
                     elif cho2 == 'ㄷ': chars[i+1][0] = 'ㅌ'; chars[i][2] = ''
                     elif cho2 == 'ㅂ': chars[i+1][0] = 'ㅍ'; chars[i][2] = ''
                     elif cho2 == 'ㅈ': chars[i+1][0] = 'ㅊ'; chars[i][2] = ''
                     elif cho2 == 'ㅅ': chars[i+1][0] = 'ㅆ'; chars[i][2] = '' 
                 elif jong1 == 'ㄶ':
                     if cho2 == 'ㄱ': chars[i+1][0] = 'ㅋ'; chars[i][2] = 'ㄴ'
                     elif cho2 == 'ㄷ': chars[i+1][0] = 'ㅌ'; chars[i][2] = 'ㄴ'
                     elif cho2 == 'ㅈ': chars[i+1][0] = 'ㅊ'; chars[i][2] = 'ㄴ'
                     elif cho2 == 'ㅅ': chars[i+1][0] = 'ㅆ'; chars[i][2] = 'ㄴ' 
                 elif jong1 == 'ㅀ':
                     if cho2 == 'ㄱ': chars[i+1][0] = 'ㅋ'; chars[i][2] = 'ㄹ'
                     elif cho2 == 'ㄷ': chars[i+1][0] = 'ㅌ'; chars[i][2] = 'ㄹ'
                     elif cho2 == 'ㅈ': chars[i+1][0] = 'ㅊ'; chars[i][2] = 'ㄹ'
                     elif cho2 == 'ㅅ': chars[i+1][0] = 'ㅆ'; chars[i][2] = 'ㄹ'
                 
        i += 1
        
    # [Pass 2] Palatalization & Liaison & H-Deletion
    i = 0
    while i < n - 1:
        curr = chars[i]; nxt = chars[i+1]
        if not isinstance(curr, list) or not isinstance(nxt, list): i+=1; continue
        
        jong1 = curr[2]
        cho2 = nxt[0]
        jung2 = nxt[1]
        
        # 2-1. H-Deletion
        if cho2 == 'ㅇ':
             if jong1 == 'ㅎ': chars[i][2] = ''
             elif jong1 == 'ㄶ': chars[i][2] = 'ㄴ'
             elif jong1 == 'ㅀ': chars[i][2] = 'ㄹ'
             
        jong1 = chars[i][2] # Update
        
        # 2-2. Palatalization (ㄷ,ㅌ + 이...)
        if cho2 == 'ㅇ' and jung2 in ['ㅣ', 'ㅑ', 'ㅕ', 'ㅛ', 'ㅠ', 'ㅖ', 'ㅒ']:
            if jong1 == 'ㄷ': chars[i+1][0] = 'ㅈ'; chars[i][2] = ''
            elif jong1 == 'ㅌ': chars[i+1][0] = 'ㅊ'; chars[i][2] = ''
            elif jong1 == 'ㄾ': chars[i+1][0] = 'ㅊ'; chars[i][2] = 'ㄹ'
            
        # 2-3. Liaison (단, 'ㅇ' 받침[ŋ]은 연음되지 않음)
        if chars[i][2] and chars[i+1][0] == 'ㅇ' and chars[i][2] != 'ㅇ':
             j = chars[i][2]
             if j in hangul.CHOSUNG:
                 chars[i+1][0] = j; chars[i][2] = ''
             elif j == 'ㄳ': chars[i+1][0] = 'ㅅ'; chars[i][2] = 'ㄱ'
             elif j == 'ㄵ': chars[i+1][0] = 'ㅈ'; chars[i][2] = 'ㄴ'
             elif j == 'ㄶ': chars[i+1][0] = 'ㄴ'; chars[i][2] = ''
             elif j == 'ㄺ': chars[i+1][0] = 'ㄱ'; chars[i][2] = 'ㄹ'
             elif j == 'ㄻ': chars[i+1][0] = 'ㅁ'; chars[i][2] = 'ㄹ'
             elif j == 'ㄼ': chars[i+1][0] = 'ㅂ'; chars[i][2] = 'ㄹ' # 넓어 -> 널버 (usually)
             elif j == 'ㄽ': chars[i+1][0] = 'ㅅ'; chars[i][2] = 'ㄹ'
             elif j == 'ㄾ': chars[i+1][0] = 'ㅌ'; chars[i][2] = 'ㄹ'
             elif j == 'ㄿ': chars[i+1][0] = 'ㅍ'; chars[i][2] = 'ㄹ'
             elif j == 'ㅀ': chars[i+1][0] = 'ㄹ'; chars[i][2] = ''
             elif j == 'ㅄ': chars[i+1][0] = 'ㅆ'; chars[i][2] = 'ㅂ' # 값이 -> 갑씨

        i += 1
        
    # [Pass 3] Normalization & Cluster Simplification (Preserve original for tense logic)
    for i in range(n):
        if not isinstance(chars[i], list): continue
        
        # Check if simplification needed (followed by Con or End)
        next_is_consonant = False
        if i+1 < n and isinstance(chars[i+1], list):
             if chars[i+1][0] != 'ㅇ': next_is_consonant = True
        elif i == n-1: next_is_consonant = True
             
        if next_is_consonant or i == n-1:
             jong = chars[i][2]
             if not jong: continue
             
             next_cho = chars[i+1][0] if i+1 < n and isinstance(chars[i+1], list) else ''
             
             # Simplify
             simple_jong = simplify_cluster(jong, next_cho)
             # Neutralize
             neutral_jong = JONG_NEUTRAL.get(simple_jong, simple_jong)
             
             chars[i][2] = neutral_jong
             
    # [Pass 4] Tensification (경음화)
    # Using original_jongs to detect ㄵ(->ㄴ), ㄺ(->ㄹ/ㄱ) cases
    # 로마자 표기 시 표준 발음에 따라 적는 것이 원칙.
    # - 용언 어간 경음화 (읽고→일꼬→ilkko): 반영
    # - 체언 합성어 경음화 (압구정→압꾸정→apgujeong): 미반영 (관용)
    for i in range(n - 1):
        curr = chars[i]; nxt = chars[i+1]
        if not isinstance(curr, list) or not isinstance(nxt, list): continue
        
        jong1 = curr[2] # Normalized
        cho2 = nxt[0]
        
        if not jong1: continue
        
        should_tensify = False
        
        # 4-1. Post-Obstruent Tensification (Standard)
        # 로마자 표기 시 체언 합성어 경음화는 반영하지 않음 (예: 압구정)
        if jong1 in ['ㄱ', 'ㄷ', 'ㅂ'] and cho2 in ['ㄱ', 'ㄷ', 'ㅂ', 'ㅅ', 'ㅈ']:
            if not is_romanization:
                should_tensify = True
            else:
                # Check POS via char_pos_map if morph_analyzer was provided
                pos_curr = char_pos_map.get(i, "")
                pos_next = char_pos_map.get(i+1, "")
                # 합성어 경음화: 체언(N) 뒤 체언(N) or 자음 -> 관용적 표기 유지
                if pos_curr.startswith("V") or pos_next.startswith("V"):
                    should_tensify = True  # 용언 어간 + 어미 경음화는 반영
                elif not pos_curr and not pos_next:
                    should_tensify = False  # 형태소 정보 없음 -> 미반영
                 
        # 4-2. Verb Stem Tensification (Heuristic with Original Jong)
        # 앉다(ㄵ), 읽고(ㄺ), 핥다(ㄾ), 읊다(ㄿ) ...
        # 용언 어간 경음화는 로마자 표기에도 반영
        orig = original_jongs.get(i, '')
        
        if orig in ['ㄵ', 'ㄶ', 'ㄻ', 'ㄼ', 'ㄾ', 'ㅀ']:
            if cho2 in ['ㄱ', 'ㄷ', 'ㅅ', 'ㅈ']:
                should_tensify = True
        
        # 4-3. Specific case rule: ㄺ (읽고 -> 일꼬)
        # 용언 어간 ㄺ 경음화도 로마자 표기에 반영
        if jong1 == 'ㄹ' and cho2 in ['ㄱ', 'ㄷ', 'ㅅ', 'ㅈ']:
             if orig in ['ㄺ', 'ㄼ', 'ㄾ', 'ㅀ']:
                  should_tensify = True
                  
        if should_tensify:
             tens_map = {'ㄱ':'ㄲ', 'ㄷ':'ㄸ', 'ㅂ':'ㅃ', 'ㅅ':'ㅆ', 'ㅈ':'ㅉ'}
             if cho2 in tens_map:
                 chars[i+1][0] = tens_map[cho2]
             
    # [Pass 5] Assimilation (Nasal/Liquid)
    for i in range(n - 1):
        curr = chars[i]; nxt = chars[i+1]
        if not isinstance(curr, list) or not isinstance(nxt, list): continue
        
        jong1 = curr[2]
        cho2 = nxt[0]
        
        # Liquidization
        if jong1 == 'ㄴ' and cho2 == 'ㄹ': chars[i][2] = 'ㄹ'; chars[i+1][0] = 'ㄹ'
        elif jong1 == 'ㄹ' and cho2 == 'ㄴ': chars[i+1][0] = 'ㄹ'
            
        # Nasalization of Liquids (Obstruent + ㄹ -> ... + ㄴ)
        if jong1 in ['ㄱ', 'ㄷ', 'ㅂ', 'ㅁ', 'ㅇ'] and cho2 == 'ㄹ':
            chars[i+1][0] = 'ㄴ'
            cho2 = 'ㄴ'
            
        # Nasalization of Obstruents
        if jong1 in ['ㄱ', 'ㄷ', 'ㅂ'] and cho2 in ['ㄴ', 'ㅁ']:
            if jong1 == 'ㄱ': chars[i][2] = 'ㅇ'
            elif jong1 == 'ㄷ': chars[i][2] = 'ㄴ'
            elif jong1 == 'ㅂ': chars[i][2] = 'ㅁ'
            
    return "".join(hangul.compose(*c) if isinstance(c, list) else c for c in chars)

def pronounce_korean(text: str) -> str:
    return pronounce(text)
