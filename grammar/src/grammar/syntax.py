from enum import Enum, auto
from typing import List, Tuple, Dict, Optional
import os
import json
from collections import defaultdict
from .utils import get_data_dir


class SentenceComponent(Enum):
    """문장 성분 (Sentence Component)"""

    SUBJECT = "주어"  # Subject (이/가, 은/는)
    OBJECT = "목적어"  # Object (을/를)
    PREDICATE = "서술어"  # Predicate (Verbs, Adjectives)
    ADVERBIAL = "부사어"  # Adverbial (에, 에서, 로, ...)
    DETERMINER = "관형어"  # Determiner (의, ㄴ/은/는/ㄹ/을)
    INDEPENDENT = "독립어"  # Independent (Vocative, Interjection)
    COMPLEMENT = "보어"  # Complement (이/가 + 되다/아니다)
    PUNCTUATION = "문장부호"  # Punctuation (SF, SP, SS, SE, SO, SW)
    UNKNOWN = "미분류"  # Unknown


DEPREL_MAP = {
    # Universal Dependencies (UD)
    "nsubj": SentenceComponent.SUBJECT,
    "obj": SentenceComponent.OBJECT,
    "iobj": SentenceComponent.ADVERBIAL,  # Indirect object -> Adverbial in KR usually
    "root": SentenceComponent.PREDICATE,
    "advmod": SentenceComponent.ADVERBIAL,
    "advcl": SentenceComponent.ADVERBIAL,
    "det": SentenceComponent.DETERMINER,
    "amod": SentenceComponent.DETERMINER,
    "acl": SentenceComponent.DETERMINER,
    "dislocated": SentenceComponent.SUBJECT,
    "fixed": SentenceComponent.PREDICATE,
    "aux": SentenceComponent.PREDICATE,
    "cc": SentenceComponent.ADVERBIAL,
    "punct": SentenceComponent.PUNCTUATION,
    # Essential Missing UD Tags
    "obl": SentenceComponent.ADVERBIAL,  # Oblique nominal (e.g., 에/에서/로)
    "nmod": SentenceComponent.DETERMINER,  # Nominal modifier (e.g., 의) - can be Adverbial too
    "appos": SentenceComponent.DETERMINER,  # Appositional modifier
    "nummod": SentenceComponent.DETERMINER,  # Numeric modifier
    "csubj": SentenceComponent.SUBJECT,  # Clausal subject
    "ccomp": SentenceComponent.OBJECT,  # Clausal complement (can be Object or Adverbial)
    "xcomp": SentenceComponent.ADVERBIAL,  # Open clausal complement
    "cop": SentenceComponent.PREDICATE,  # Copula (이다/아니다) - handled as Predicate?
    "case": SentenceComponent.DETERMINER,  # Case marker (postposition) - usually dependent on head
    "mark": SentenceComponent.ADVERBIAL,  # Marker (conjunction)
    "flat": SentenceComponent.PREDICATE,  # Flat structure
    "parataxis": SentenceComponent.ADVERBIAL,  # Parataxis
    "compound": SentenceComponent.PREDICATE,  # Compound
    "vocative": SentenceComponent.INDEPENDENT,  # Vocative
    "discourse": SentenceComponent.INDEPENDENT,  # Discourse
    "orphan": SentenceComponent.UNKNOWN,
    "reparandum": SentenceComponent.UNKNOWN,
    "clf": SentenceComponent.DETERMINER,  # Classifier
    "list": SentenceComponent.UNKNOWN,
    # Sejong / ETRI Tags (Common variations)
    "NP_SBJ": SentenceComponent.SUBJECT,
    "NP_OBJ": SentenceComponent.OBJECT,
    "NP_MOD": SentenceComponent.ADVERBIAL,  # Can be determiner, but often modifying predicate
    "NP_AJT": SentenceComponent.ADVERBIAL,
    "VP": SentenceComponent.PREDICATE,
    "VP_MOD": SentenceComponent.ADVERBIAL,
    "VNP": SentenceComponent.PREDICATE,
    "NP_CNJ": SentenceComponent.ADVERBIAL,  # Conjunction
}


class SyntaxAnalyzer:
    """
    구문 분석기 (Syntax Analyzer)
    형태소 분석 결과를 바탕으로 문장 성분을 추론합니다.
    통계적 학습(Pattern Learning)을 지원합니다.
    """

    def __init__(self, use_neural=False):
        # Learned Patterns: {"NNG+JKS": "SUBJECT", ...}
        self.learned_counts = defaultdict(lambda: defaultdict(int))
        self.learned_patterns = {}
        self._load_model()

        self.neural_model = None
        if use_neural:
            try:
                from .neural_wrapper import NeuralWrapper

                self.neural_model = NeuralWrapper()
            except Exception as e:
                print(f"Warning: Failed to load Neural Syntax Model: {e}")

    def train_pattern(self, pos_sequence: str, deprel: str):
        """
        패턴 학습

        Args:
            pos_sequence: 품사 시퀀스 (예: "NNG+JKS")
            deprel: 의존 관계 레이블 (예: "nsubj" or "NP_SBJ" or "주어")
        """
        # 1. Map DEPREL to Component
        component = DEPREL_MAP.get(deprel)

        # 2. If not found, check if deprel matches Enum value directly (e.g. "주어")
        if component is None:
            for member in SentenceComponent:
                if member.value == deprel or member.name == deprel.upper():
                    component = member
                    break

        # 3. If still unknown, fallback
        if component is None:
            component = SentenceComponent.UNKNOWN
            # Optional: Log unknown deprel if needed
            return

        self.learned_counts[pos_sequence][component.name] += 1

        # Update best pattern immediately (Online learning)
        best_comp = max(
            self.learned_counts[pos_sequence], key=self.learned_counts[pos_sequence].get
        )
        self.learned_patterns[pos_sequence] = best_comp

    def save_model(self):
        """학습된 패턴 저장"""
        model_path = os.path.join(get_data_dir(), "syntax_patterns.json")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # Convert to serializable format
        data = {"patterns": self.learned_patterns}

        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_model(self):
        model_path = os.path.join(get_data_dir(), "syntax_patterns.json")
        if os.path.exists(model_path):
            try:
                with open(model_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.learned_patterns = data.get("patterns", {})
            except Exception:
                pass

    def analyze(
        self,
        morphemes: List[Tuple[str, str]] = None,
        text: str = None,
        morph_analyzer=None,
    ) -> List[Tuple[str, str, SentenceComponent]]:
        """
        형태소 분석 결과를 입력받아 문장 성분을 분석합니다.

        Args:
            morphemes: (surface, pos) 튜플의 리스트 (Legacy)
            text: 원본 문장 텍스트 (Optional, 권장)
            morph_analyzer: MorphAnalyzer 인스턴스 (text 사용 시 필수)

        Returns:
            (word, pos_sequence, component) 튜플의 리스트
            - word: 어절 (Word/Chunk)
            - pos_sequence: 해당 어절의 형태소 품사 나열 (예: "NNG+JKS")
            - component: 문장 성분 (SentenceComponent)
        """
        # 0. Neural Analysis (Whole Sentence)
        if self.neural_model and text and morph_analyzer:
            # 1. Morphological Analysis (Full Sentence)
            # Need flat list of morphemes
            full_morphemes = []
            eojeols = text.split()
            # Creating mapping to align back to eojeols if needed,
            # but Neural Model predicts per-morpheme Syntax.
            # SyntaxAnalyzer return format: (word, pos_seq, component)
            # This format assumes "Word" (Eojeol) based output.
            # But the Neural Model (and UD) works on "Units" (Morphemes).

            # Let's try to map Neural Output back to Eojeols.

            # ... For now, stick to hybrid/chunk approach unless we fully overhaul the return signature.
            # Actually, `analyze` returns list of (word, pos, component).
            # If we simply pass the morphemes of the current chunk to neural model, it lacks context.
            # Ideally we pass the WHOLE sentence morphemes to Neural Model.

            # Collect all morphemes first
            all_morphs_flat = []
            chunk_indices = []  # (start_idx, end_idx) in flat list for each eojeol

            current_idx = 0
            for eojeol in eojeols:
                morphs = morph_analyzer.analyze(eojeol)  # List of (surf, pos)
                if not morphs:
                    morphs = [(eojeol, "UNKNOWN")]

                all_morphs_flat.extend(m[0] for m in morphs)
                chunk_indices.append((current_idx, current_idx + len(morphs)))
                current_idx += len(morphs)

            # Predict
            predictions = self.neural_model.predict(all_morphs_flat)

            if predictions:
                # Map back to Eojeol results
                results = []
                for i, (start, end) in enumerate(chunk_indices):
                    # Combine results for this eojeol
                    chunk_preds = predictions[start:end]

                    word = eojeols[i]
                    # POS Sequence
                    pos_seq = "+".join(p["pos"] for p in chunk_preds)

                    # Component Determination from Dependency Labels (DEPREL)
                    # Heuristic: The 'head' of the Eojeol determines its role?
                    # Or the relation of the *last* morpheme (usually Josa/Ending) determines the role.
                    # Korean is head-final in Eojeol structure.
                    last_pred = chunk_preds[-1]
                    deprel = last_pred["deprel"]

                    # Map deprel to Component
                    component = DEPREL_MAP.get(deprel, SentenceComponent.UNKNOWN)

                    # Fallback mapping
                    if component == SentenceComponent.UNKNOWN:
                        # Try mapping from name
                        for member in SentenceComponent:
                            if member.value == deprel or member.name == deprel.upper():
                                component = member
                                break

                    if component == SentenceComponent.UNKNOWN:
                        # Heuristic Fallback using POS tags (Enhancement)
                        # Support both Sejong (JKS, etc.) and UD (ADP, PART, etc.)

                        is_subject_marker = False
                        is_object_marker = False
                        is_adverb_marker = False

                        # Check specific words if POS is generic (ADP/PART)
                        if "은" in word or "는" in word or "이" in word or "가" in word:
                            is_subject_marker = True
                        if "을" in word or "를" in word:
                            is_object_marker = True
                        if "에" in word or "로" in word or "서" in word or "와" in word:
                            is_adverb_marker = True

                        if (
                            "JKS" in pos_seq
                            or ("ADP" in pos_seq and is_subject_marker)
                            or ("PART" in pos_seq and is_subject_marker)
                        ):
                            component = SentenceComponent.SUBJECT
                        elif "JKO" in pos_seq or (
                            "ADP" in pos_seq and is_object_marker
                        ):
                            component = SentenceComponent.OBJECT
                        elif (
                            "JKB" in pos_seq
                            or ("ADP" in pos_seq and is_adverb_marker)
                            or "ADV" in pos_seq
                        ):
                            component = SentenceComponent.ADVERBIAL
                        elif (
                            "JKG" in pos_seq
                            or "ETM" in pos_seq
                            or "DET" in pos_seq
                            or "ADJ" in pos_seq
                        ):
                            component = SentenceComponent.DETERMINER
                        elif (
                            "EF" in pos_seq
                            or "VV" in pos_seq
                            or "VA" in pos_seq
                            or "VERB" in pos_seq
                        ):
                            component = SentenceComponent.PREDICATE
                        elif "MAG" in pos_seq or "ADV" in pos_seq:
                            component = SentenceComponent.ADVERBIAL
                        elif "NOUN" in pos_seq or "PROPN" in pos_seq:
                            # For single noun words without particle, default to Unknown or maybe Subject if typical?
                            # Let's keep UNKNOWN unless we have strong reason.
                            pass

                    if component == SentenceComponent.UNKNOWN:
                        print(f"  [DEBUG] Unknown Deprel: {deprel} for word {word}")

                    # -----------------------------------------------------------------
                    # Rule-based Correction (Hybrid approach for Maximum Accuracy)
                    # Neural models can make mistakes on long-distance dependencies or rare contexts.
                    # Korean has explicit markers (Josa/Eomi) that are strong signals.
                    # We override the neural prediction if a strong marker is present.
                    # -----------------------------------------------------------------

                    if morph_analyzer:
                        input_morphs = morph_analyzer.analyze(word)
                        if input_morphs:
                            # Use reliable input POS
                            pos_seq = "+".join(m[1] for m in input_morphs)

                    if "JKO" in pos_seq:
                        component = SentenceComponent.OBJECT
                    elif "JKS" in pos_seq:
                        component = SentenceComponent.SUBJECT
                    # JX (Auxiliary Particle) is tricky, but often Subject/Topic in simple sentences.
                    # Only override if current prediction seems very wrong (e.g. Predicate/Adverbial for a Noun+JX)
                    elif "JX" in pos_seq and component in [
                        SentenceComponent.PREDICATE,
                        SentenceComponent.ADVERBIAL,
                    ]:
                        component = SentenceComponent.SUBJECT
                    elif "JKB" in pos_seq:
                        component = SentenceComponent.ADVERBIAL
                    elif "JKG" in pos_seq:
                        component = SentenceComponent.DETERMINER
                    elif "EF" in pos_seq and component != SentenceComponent.PREDICATE:
                        component = SentenceComponent.PREDICATE

                    results.append((word, pos_seq, component))

                return results

        # 1. 텍스트와 분석기가 제공된 경우 (권장 방식: 띄어쓰기 보존)
        if text and morph_analyzer:
            results = []
            eojeols = text.split()

            for eojeol in eojeols:
                # 각 어절 독립 분석
                # morph_analyzer.analyze(eojeol)은 전체 리스트를 반환하므로,
                # 여기서는 단일 어절임이 보장되므로 그대로 사용
                chunk_morphemes = morph_analyzer.analyze(eojeol)

                if not chunk_morphemes:
                    # 분석 실패 시 그대로 반환
                    results.append((eojeol, "UNKNOWN", SentenceComponent.UNKNOWN))
                    continue

                pos_seq = "+".join(m[1] for m in chunk_morphemes)
                component = self._determine_component(chunk_morphemes)
                results.append((eojeol, pos_seq, component))

            # 보어 처리
            self._refine_complements(results)
            return results

        # 2. 형태소 리스트만 제공된 경우 (Legacy: 띄어쓰기 정보 소실 가능성 있음)
        if not morphemes:
            return []

        # 어절 단위로 그룹화 (휴리스틱)
        chunks = self._group_into_chunks(morphemes)

        # 각 덩어리의 문장 성분 결정
        results = []
        for chunk_morphemes in chunks:
            word = "".join(m[0] for m in chunk_morphemes)
            pos_seq = "+".join(m[1] for m in chunk_morphemes)
            component = self._determine_component(chunk_morphemes)
            results.append((word, pos_seq, component))

        # 보어 처리
        self._refine_complements(results)

        return results

    def _group_into_chunks(
        self, morphemes: List[Tuple[str, str]]
    ) -> List[List[Tuple[str, str]]]:
        """형태소 리스트를 의미 단위(어절 유사)로 그룹화"""
        chunks = []
        current_chunk = []

        for i, (surf, pos) in enumerate(morphemes):
            if not current_chunk:
                current_chunk.append((surf, pos))
                continue

            prev_surf, prev_pos = current_chunk[-1]

            # 연결 규칙
            is_noun_josa = prev_pos.startswith("N") and pos.startswith(
                "J"
            )  # 체언 + 조사
            is_verb_ending = (
                prev_pos.startswith("V") or prev_pos.startswith("EP")
            ) and (
                pos.startswith("E") or pos.startswith("EP")
            )  # 용언/선어말어미 + 어미/선어말어미
            is_affix = pos.startswith("X")  # 접사 (XSN, XSV, XSA)

            # 이전이 조사인데 또 조사가 오는 경우 (조사 결합)
            is_josa_josa = prev_pos.startswith("J") and pos.startswith("J")

            if is_noun_josa or is_verb_ending or is_affix or is_josa_josa:
                current_chunk.append((surf, pos))
            else:
                # 새로운 덩어리 시작
                chunks.append(current_chunk)
                current_chunk = [(surf, pos)]

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _determine_component(self, chunk: List[Tuple[str, str]]) -> SentenceComponent:
        """단일 덩어리의 문장 성분 결정"""
        if not chunk:
            return SentenceComponent.UNKNOWN

        # 0. Check Learned Patterns
        pos_seq = "+".join(pos for _, pos in chunk)
        if pos_seq in self.learned_patterns:
            comp_name = self.learned_patterns[pos_seq]
            return SentenceComponent[comp_name]

        # 1. 전체가 문장 부호인지 확인
        is_all_punctuation = all(p.startswith("S") for _, p in chunk)
        if is_all_punctuation:
            return SentenceComponent.PUNCTUATION

        # 2. 분석을 위해 끝에 붙은 문장 부호 제거 (예: "갔습니다." -> "갔습니다")
        # 문장 부호가 아닌 마지막 형태소를 찾음
        effective_chunk = [m for m in chunk if not m[1].startswith("S")]

        if not effective_chunk:
            # 문장 부호만 있는 경우는 위에서 처리했으므로, 여기는 도달하지 않아야 함
            # 하지만 안전을 위해 처리
            return SentenceComponent.PUNCTUATION

        last_surf, last_pos = effective_chunk[-1]

        # 3. 서술어 (용언으로 끝남)
        # 어미(EF, EC, ETN, ETM)로 끝나는 경우도 서술어의 활용형일 수 있음
        # 하지만 관형사형 전성어미(ETM)은 관형어, 명사형 전성어미(ETN)은 명사 역할(주어/목적어 등)을 할 수 있음.
        # 여기서는 단순화하여 처리

        has_verb = any(
            p.startswith("V") or p.startswith("XSV") or p.startswith("XSA")
            for _, p in effective_chunk
        )

        if last_pos.startswith("EF"):  # 종결 어미 -> 서술어
            return SentenceComponent.PREDICATE

        if last_pos == "ETM":  # 관형사형 전성어미 -> 관형어
            return SentenceComponent.DETERMINER

        # 2. 체언 + 조사
        if last_pos.startswith("J"):
            # 조사 그룹 내에서 가장 의미있는 격조사 찾기 (뒤에서부터)
            # 예: "학교에서조차" -> "에서"(JKB) + "조차"(JX) -> Adverbial
            # 마지막이 JX이면 그 앞의 조사를 확인

            # chunk에서 조사만 추출 (뒤에서부터)
            reversed_particles = []
            for m in reversed(chunk):
                if m[1].startswith("J"):
                    reversed_particles.append(m)
                else:
                    break  # 조사가 아니면 중단 (체언 등)

            # 우선순위: JKB/JKO/JKS > JX
            # JX만 있으면 Subject 등 기본값.

            final_decision = None

            for surf, pos in reversed_particles:
                if pos == "JKB":  # 부사격
                    return SentenceComponent.ADVERBIAL
                elif pos == "JKO":  # 목적격
                    return SentenceComponent.OBJECT
                elif pos == "JKS":  # 주격
                    return SentenceComponent.SUBJECT
                elif pos == "JKG":  # 관형격
                    return SentenceComponent.DETERMINER
                elif pos == "JKC":  # 보격
                    return SentenceComponent.COMPLEMENT
                elif pos == "JKV":  # 호격
                    return SentenceComponent.INDEPENDENT

            # 격조사가 없으면 JX 처리
            if last_pos == "JX":
                if last_surf in ["은", "는", "도", "만", "조차", "마저", "부터"]:
                    # 보조사는 문맥에 따라 다르지만 기본적으로 주어 역할을 많이 함 (은/는)
                    # "조차", "마저", "부터"는 부사어일 수도 있지만 주어 자리에도 옴.
                    # 여기서는 안전하게 SUBJECT로 하되, Unknown 보다는 나음.
                    return SentenceComponent.SUBJECT

            if last_pos == "JC":
                return SentenceComponent.ADVERBIAL  # 와/과

        # 3. 부사 (MAG, MAJ)
        if any(p.startswith("MA") for _, p in chunk):
            return SentenceComponent.ADVERBIAL

        # 4. 관형사 (MM)
        if any(p == "MM" for _, p in chunk):
            return SentenceComponent.DETERMINER

        # 5. 감탄사 (IC)
        if any(p == "IC" for _, p in chunk):
            return SentenceComponent.INDEPENDENT

        # 6. 문장 부호 (S...) -> 위에서 처리함

        # 기본값: 명사 단독이면 주어/목적어/보어 등을 알 수 없음 (무표).
        # 문맥 없이 단독 명사는 보통 주어/목적어보다는 표제어 성격이 강함.
        # 여기서는 UNKNOWN 또는 문맥에 맡김.
        if has_verb:
            return SentenceComponent.PREDICATE

        return SentenceComponent.UNKNOWN

    def _refine_complements(self, results: List[Tuple[str, str, SentenceComponent]]):
        """
        보어(Complement) 후처리
        '되다', '아니다' 앞의 '이/가'는 주어가 아니라 보어임.
        """
        for i in range(len(results) - 1):
            word, pos, component = results[i]
            next_word, next_pos, next_component = results[i + 1]

            # 현재 성분이 주어(JKS/JKC)이고, 다음 단어가 '되다' 또는 '아니다'인 경우
            if component == SentenceComponent.SUBJECT:
                # 다음 단어의 기본형 확인 (단순화: '되' 또는 '아니'로 시작하는 용언)
                if "되" in next_word or "아니" in next_word:
                    # 엄밀히는 형태소 분석 원형을 봐야 하지만, surface로 약식 체크
                    # JKS(이/가)가 붙어있으면 보어로 변경
                    if "JKS" in pos or "JKC" in pos:
                        results[i] = (word, pos, SentenceComponent.COMPLEMENT)
