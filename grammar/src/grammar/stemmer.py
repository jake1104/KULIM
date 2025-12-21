from typing import List, Tuple, Optional
from dataclasses import dataclass
import math

try:
    from .conjugation import ConjugationAnalyzer
    from .irregular import IrregularConjugation
    from .constraints import ConstraintValidator
    from .scorers import SCORING
except ImportError:
    from conjugation import ConjugationAnalyzer
    from irregular import IrregularConjugation
    from constraints import ConstraintValidator
    from scorers import SCORING


from .morph import Morph


class Stemmer:
    """v03 형태소 분석 엔진"""

    """v03 형태소 분석 엔진"""

    def __init__(self, trie, use_gpu=False, use_rust=False):
        self.trie = trie
        self.conjugation = ConjugationAnalyzer(trie)
        self.irregular = IrregularConjugation()
        self.use_gpu = use_gpu
        self.use_rust = use_rust
        self.constraints = ConstraintValidator()

    def analyze(self, text: str) -> List[List[Morph]]:
        import re

        # Split by period more aggressively to ensure punctuation is treated as separate token
        # Regex explanation: Split by ([.]) -> captures delimiter.
        # "갔다." -> ['갔다', '.', '']
        sentences = re.split(r"([.!?。])", text)
        results = []
        for sent in sentences:
            sent = sent.strip()
            if sent:
                morphemes = self._analyze_sentence(sent)
                results.append(morphemes)
        return results

    def _analyze_sentence(self, sentence: str) -> List[Morph]:
        """문맥 인식 DP 분석 - HMM 우선"""
        if not sentence:
            return []

        # Rust Optimization
        if self.use_rust and hasattr(self.trie, "analyze"):  # Enable Rust Viterbi
            rust_results = self.trie.analyze(sentence)
            if rust_results:
                final_morphemes = []
                for surface, pos, lemma in rust_results:
                    if "+" in pos:
                        # Recursive decomposition (e.g. VV+EP+EF+SF -> VV, EP, EF, SF)
                        pos_parts = pos.split("+")
                        lemma_parts = lemma.split("+")

                        # Just in case lemma parts count mismatches (heuristic fallback)
                        if len(pos_parts) != len(lemma_parts):
                            # Fallback: assign lemma=surface to each or split by char if matching?
                            # For safety, assign remaining lemma to last part or reuse lemma
                            # Correct "training" should ensure consistency.
                            # If irregular learning was done right: "가+았+다+."
                            pass

                        # We cannot know exact surface boundary for each part easily without alignment data
                        # BUT, for output visual, we often show "가/VV + 았/EP" etc.
                        # The user wants "분리된 형태소".
                        # Lemma is key. Surface for *sub-morphemes* is often the lemma form for irreg.
                        # e.g. "가/VV", "았/EP".

                        for i, (p, l) in enumerate(zip(pos_parts, lemma_parts)):
                            final_morphemes.append(Morph(l, p, l))
                            # Note: Setting surface=lemma for decomposed parts is standard unique representation
                            # unless we have exact surface span alignment.
                    else:
                        final_morphemes.append(Morph(surface, pos, lemma))
                return final_morphemes

        n = len(sentence)
        dp = [float("inf")] * (n + 1)
        path = [None] * (n + 1)
        prev_pos = [None] * (n + 1)
        dp[0] = 0.0

        for i in range(n):
            if dp[i] == float("inf"):
                continue

            # Trie 검색
            patterns = self.trie.search_all_patterns(sentence[i : min(i + 16, n)])

            for start, end, pattern_list in patterns:
                if start != 0:
                    continue

                j = i + end
                surface = sentence[i:j]

                for pos, lemma in pattern_list:
                    # 제약 조건 검사
                    if prev_pos[i]:
                        if not self.constraints.is_valid_transition(prev_pos[i], pos):
                            continue

                    word_len = len(surface)
                    base_cost = SCORING.get_length_cost(word_len)

                    # 단음절 동사/감탄사 페널티
                    if word_len == 1 and (pos.startswith("V") or pos == "IC"):
                        base_cost += SCORING.PENALTY_SINGLE_VERB_IC

                    # 일반 명사 보너스
                    if pos.startswith("N") and word_len >= 2:
                        base_cost -= SCORING.BONUS_NOUN_2PLUS

                    # 부사 보너스 (일반화된 규칙)
                    if pos == "MAG" and word_len >= 2:
                        base_cost -= (
                            SCORING.BONUS_ADVERB_2PLUS
                        )  # 명사보다 우선순위 높임

                    # 문맥 기반 비용 (Transition Cost)
                    # 모델에서 전환 비용을 가져옴 (Log Prob 등)
                    # 이전 로직은 Bonus를 빼는 방식이었지만, get_transition_cost는 "Cost"를 반환한다고 가정.
                    # (TransitionModel 기본값은 Penalty 10.0, 학습된 값은 낮음/음수)
                    context_cost = 0.0
                    if prev_pos[i]:
                        prev = prev_pos[i]
                        context_cost = SCORING.get_transition_cost(prev, pos)

                    # Total Cost = Base + Context + ...
                    # Note: get_transition_cost generally returns positive penalty for unseen,
                    # negative (log prob) or low for seen.
                    # Previous logic was `total_cost - bonus`.
                    # Here we treat it as additive cost.
                    # Adjust variable usage below.

                    total_cost = dp[i] + base_cost + context_cost

                    if total_cost < dp[j]:
                        dp[j] = total_cost

                        if "+" in pos:
                            # Composite Tag Decomposition (e.g. VV+EP+EF+SF)
                            # Create nested Morpheme structure or just use sub_morphemes
                            # But Viterbi path stores a single Morpheme object at [j]
                            # So we create a parent Morpheme representing the Surface,
                            # containing sub_morphemes.

                            pos_parts = pos.split("+")
                            lemma_parts = lemma.split("+")

                            sub_morphemes = []
                            # Heuristic: if counts match, assign 1-to-1
                            if len(pos_parts) == len(lemma_parts):
                                for p, l in zip(pos_parts, lemma_parts):
                                    sub_morphemes.append(Morph(l, p, l))
                            else:
                                # Fallback: Treat as one block or use surface for all?
                                # If mismatch, just store as is to avoid crash, OR
                                # try to split surface if possible (hard without lengths).
                                # Use lemma as surface for subs.
                                for p in pos_parts:
                                    sub_morphemes.append(Morph(lemma, p, lemma))

                            # Create wrapper morpheme
                            path[j] = Morph(
                                surface, pos, lemma, sub_morphs=sub_morphemes
                            )
                            # For next transition, use the LAST POS of the sequence
                            prev_pos[j] = pos_parts[-1]
                        else:
                            path[j] = Morph(surface, pos, lemma)
                            prev_pos[j] = pos

            # Conjugation 시도
            for j in range(i + 1, min(i + 8, n + 1)):
                surface = sentence[i:j]
                conj_results = self.conjugation.restore_verb_stem(surface)

                for stem, ending in conj_results:
                    if not ending:
                        continue

                    stem_patterns = self.trie.search_all_patterns(stem)

                    for s_start, s_end, s_patterns in stem_patterns:
                        if s_start == 0 and s_end == len(stem):
                            for pos, lemma in s_patterns:
                                if pos.startswith("V"):
                                    # 제약조건: Prev -> Stem
                                    if prev_pos[
                                        i
                                    ] and not self.constraints.is_valid_transition(
                                        prev_pos[i], pos
                                    ):
                                        continue

                                    base_cost = SCORING.COST_CONJUGATION_BASE

                                    context_cost = 0.0
                                    if prev_pos[i]:
                                        prev = prev_pos[i]
                                        context_cost = SCORING.get_transition_cost(
                                            prev, pos
                                        )

                                    hmm_score = 0.0

                                    # 어미 POS 추정 (휴리스틱)
                                    ending_pos = "EP"
                                    if ending in [
                                        "은",
                                        "는",
                                        "을",
                                        "ㄹ",
                                        "던",
                                        "ㄴ",
                                    ]:
                                        ending_pos = "ETM"
                                    elif ending in [
                                        "다",
                                        "요",
                                        "죠",
                                        "습니다",
                                        "ㅂ니다",
                                        "구나",
                                        "군",
                                    ]:
                                        ending_pos = "EF"
                                    elif ending in [
                                        "고",
                                        "며",
                                        "면서",
                                        "아",
                                        "어",
                                        "게",
                                        "지",
                                        "니",
                                        "니까",
                                    ]:
                                        ending_pos = "EC"
                                    elif ending in ["았", "었", "겠", "시"]:
                                        ending_pos = "EP"

                                    total_cost = dp[i] + base_cost + context_cost

                                    if total_cost < dp[j]:
                                        dp[j] = total_cost
                                        stem_morph = Morph(stem, pos, lemma)

                                        ending_morph = Morph(ending, ending_pos, ending)
                                        path[j] = Morph(
                                            surface,
                                            pos,  # VV or VA
                                            lemma,
                                            sub_morphs=[stem_morph, ending_morph],
                                        )
                                        prev_pos[j] = ending_pos
                                    break
                            break
            # 미등록어
            for j in range(i + 1, min(i + 16, n + 1)):
                if dp[j] == float("inf"):
                    surface = sentence[i:j]
                    cost = SCORING.COST_OOV
                    total_cost = dp[i] + cost
                    if total_cost < dp[j]:
                        dp[j] = total_cost
                        path[j] = Morph(surface, "NNG", surface, 0.5)
                        prev_pos[j] = "NNG"

        return self._backtrack(path, n)

    def _backtrack(self, path, end):
        """역추적"""
        result = []
        current = end
        while current > 0 and path[current]:
            morph = path[current]
            if morph.sub_morphs:
                for sub in reversed(morph.sub_morphs):
                    result.append(sub)
            else:
                result.append(morph)
            current -= len(morph.surface)
        result.reverse()
        return result
