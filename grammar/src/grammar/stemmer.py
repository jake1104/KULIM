from typing import List, Tuple, Optional
import math
import re

from .conjugation import ConjugationAnalyzer
from .irregular import IrregularConjugation
from .constraints import ConstraintValidator
from .scorers import SCORING
from .morph import Morph


class Stemmer:
    def __init__(self, trie, use_gpu=False, use_rust=False):
        self.trie = trie
        self.conjugation = ConjugationAnalyzer(trie)
        self.irregular = IrregularConjugation()
        self.use_gpu = use_gpu
        self.use_rust = use_rust
        self.constraints = ConstraintValidator()

    def analyze(self, text: str) -> List[List[Morph]]:
        sentences = re.split(r"([.!?。])", text)
        results = []
        for sent in sentences:
            sent = sent.strip()
            if sent:
                morphemes = self._analyze_sentence(sent)
                results.append(morphemes)
        return results

    def _analyze_sentence(self, sentence: str) -> List[Morph]:
        if not sentence:
            return []

        if self.use_rust and hasattr(self.trie, "analyze"):
            rust_results = self.trie.analyze(sentence)
            if rust_results:
                return self._process_rust_results(rust_results)

        n = len(sentence)
        dp = [float("inf")] * (n + 1)
        path = [None] * (n + 1)
        prev_pos = [None] * (n + 1)
        dp[0] = 0.0

        for i in range(n):
            if dp[i] == float("inf"):
                continue

            trie_candidates = self._get_trie_candidates(i, sentence)
            conj_candidates = self._get_conj_candidates(i, sentence)
            oov_candidates = self._get_oov_candidates(i, sentence)

            for j, pos, lemma, surface, sub_morphs, conj_bonus in trie_candidates + conj_candidates:
                if prev_pos[i] and not self.constraints.is_valid_transition(prev_pos[i], pos):
                    continue

                word_len = len(surface)
                base_cost = SCORING.get_length_cost(word_len)

                if word_len == 1 and (pos.startswith("V") or pos == "IC"):
                    base_cost += SCORING.PENALTY_SINGLE_VERB_IC
                if pos.startswith("N") and word_len >= 2:
                    base_cost -= SCORING.BONUS_NOUN_2PLUS
                if pos == "MAG" and word_len >= 2:
                    base_cost -= SCORING.BONUS_ADVERB_2PLUS

                context_cost = 0.0
                if prev_pos[i]:
                    context_cost = SCORING.get_transition_cost(prev_pos[i], pos)

                total_cost = dp[i] + base_cost + context_cost + conj_bonus

                if total_cost < dp[j]:
                    dp[j] = total_cost
                    if "+" in pos:
                        pos_parts = pos.split("+")
                        lemma_parts = lemma.split("+")
                        sub = []
                        if len(pos_parts) == len(lemma_parts):
                            for p, l in zip(pos_parts, lemma_parts):
                                sub.append(Morph(l, p, l))
                        else:
                            for p in pos_parts:
                                sub.append(Morph(lemma, p, lemma))
                        path[j] = Morph(surface, pos, lemma, sub_morphs=sub)
                        prev_pos[j] = pos_parts[-1]
                    elif sub_morphs:
                        path[j] = Morph(surface, pos, lemma, sub_morphs=sub_morphs)
                        prev_pos[j] = pos
                    else:
                        path[j] = Morph(surface, pos, lemma)
                        prev_pos[j] = pos

            if oov_candidates:
                for j, pos, lemma, surface in oov_candidates:
                    if dp[j] == float("inf"):
                        cost = SCORING.COST_OOV
                        total_cost = dp[i] + cost
                        if total_cost < dp[j]:
                            dp[j] = total_cost
                            path[j] = Morph(surface, pos, lemma, 0.3)
                            prev_pos[j] = pos

        return self._backtrack(path, n)

    def _get_trie_candidates(self, i, sentence):
        candidates = []
        max_len = min(i + 16, len(sentence))
        for j in range(i + 1, max_len + 1):
            patterns = self.trie.search_all_patterns(sentence[i:j])
            for start, end, pattern_list in patterns:
                if start != 0:
                    continue
                for pos, lemma in pattern_list:
                    candidates.append((j, pos, lemma, sentence[i:j], None, 0.0))
        return candidates

    def _get_conj_candidates(self, i, sentence):
        candidates = []
        max_len = min(i + 8, len(sentence))
        for j in range(i + 1, max_len + 1):
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
                                if ending in ["은", "는", "을", "ㄹ", "던", "ㄴ", "았던", "었던"]:
                                    ending_pos = "ETM"
                                elif ending in ["다", "요", "죠", "습니다", "ㅂ니다", "구나", "군요", "네", "아", "어", "라", "자", "마", "오", "네요", "어요", "아요", "ㄴ다", "는다"]:
                                    ending_pos = "EF"
                                elif ending in ["고", "며", "면서", "지만", "어서", "아서", "니까", "으니까", "니", "면", "으면", "게", "지", "도록", "려고", "으려고", "러", "으러", "려", "자", "도", "는데", "은데", "ㄴ데", "어도", "아도", "거든", "건", "을수록", "ㄹ수록", "으나", "든지", "든가"]:
                                    ending_pos = "EC"
                                elif ending in ["았", "었", "였", "겠", "시", "으시", "옵", "사옵"]:
                                    ending_pos = "EP"
                                elif ending in ["기", "ㅁ", "음"]:
                                    ending_pos = "ETN"
                                else:
                                    ending_pos = "EF"
                                candidates.append(
                                    (j, pos, lemma, surface,
                                     [Morph(stem, pos, lemma), Morph(ending, ending_pos, ending)],
                                     -5.0)
                                )
        return candidates

    def _get_oov_candidates(self, i, sentence):
        candidates = []
        max_len = min(i + 5, len(sentence))
        for j in range(i + 1, max_len + 1):
            surface = sentence[i:j]
            if not re.match(r'^[가-힣]+$', surface):
                continue
            guessed_pos = "NNG"
            guessed_lemma = surface
            if len(surface) >= 2 and surface.endswith("다"):
                stem = surface[:-1]
                if len(stem) >= 1:
                    guessed_pos = "VV"
                    guessed_lemma = stem
            elif len(surface) >= 3 and surface.endswith("하다"):
                guessed_pos = "VV"
                guessed_lemma = surface[:-2]
            elif len(surface) >= 3 and surface.endswith("되다"):
                guessed_pos = "VV"
                guessed_lemma = surface[:-2]
            elif len(surface) >= 3 and surface.endswith("스럽"):
                guessed_pos = "VA"
                guessed_lemma = surface
            elif len(surface) >= 2 and surface.endswith("이"):
                guessed_pos = "NNG"
                guessed_lemma = surface
            candidates.append((j, guessed_pos, guessed_lemma, surface))
        return candidates

    def _process_rust_results(self, rust_results):
        final_morphemes = []
        for surface, pos, lemma in rust_results:
            if "+" in pos:
                pos_parts = pos.split("+")
                lemma_parts = lemma.split("+")
                for i, (p, l) in enumerate(zip(pos_parts, lemma_parts)):
                    final_morphemes.append(Morph(l, p, l))
            else:
                final_morphemes.append(Morph(surface, pos, lemma))
        return final_morphemes

    def _backtrack(self, path, end):
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
