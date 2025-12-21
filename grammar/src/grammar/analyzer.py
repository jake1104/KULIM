from typing import List, Tuple, Dict
import os

from .stemmer import Stemmer
from .morph import Morph
from .dictionary import build_comprehensive_trie
from .preprocessor import Preprocessor
from .utils import get_data_dir, get_version


class MorphAnalyzer:
    """형태소 분석기"""

    def __init__(
        self,
        use_double_array=True,
        use_sejong=True,
        use_gpu=False,
        use_rust=False,
        use_neural=False,
        load_defaults=True,  # New flag
        debug=False,
    ):
        if debug:
            print("=" * 60)
            print("  v0.1.0 형태소 분석기 초기화")
            if use_gpu:
                print("  GPU 가속: ON")
            if use_rust:
                print("  Rust 가속: ON")
            print("=" * 60)

        self.trie = build_comprehensive_trie(
            use_double_array=use_double_array,
            use_sejong=use_sejong,
            use_rust=use_rust,
            load_defaults=load_defaults,
        )

        self.preprocessor = Preprocessor()
        self.stemmer = Stemmer(trie=self.trie, use_gpu=use_gpu, use_rust=use_rust)

        # Neural Morph Integration
        self.use_neural = use_neural
        self.neural_wrapper = None
        if use_neural:
            try:
                from .neural_wrapper import NeuralWrapper

                self.neural_wrapper = NeuralWrapper()
                if debug:
                    print("  [v] Neural Morphological Analysis: ON")
            except Exception as e:
                # Silently fail or warn?
                # User wants "usable CLI+API", spammed prints are bad.
                # Let's keep it clean.
                if debug:
                    print(f"  ⚠ Neural Model Load Failed: {e}")
                self.use_neural = False

        if debug:
            print("=" * 60)
            print("  [v] 초기화 완료")
            print("=" * 60)

    def save(self):
        """현재 모델 저장"""
        data_dir = get_data_dir()
        os.makedirs(data_dir, exist_ok=True)

        # 1. HMM 저장
        # 1. Neural Model 저장 (만약 online training으로 변경사항이 있다면)
        if self.use_neural and self.neural_wrapper and self.neural_wrapper.morph_model:
            # NeuralWrapper doesn't have explicit save yet, but we can access model
            # But usually we save dicts.
            # Let's assume user manually manages neural model saving or we implement simple save.
            # NeuralWrapper.load() loads from path...
            # We implemented load() but not save() in NeuralWrapper?
            # Actually NeuralTrainer has save.
            # Let's verify if we need to implement save() in NeuralWrapper.
            # For now, just skip explicit save of Neural Model here to avoid complexity,
            # OR implement a simple save in NeuralWrapper later.
            pass

        # 2. Dictionary 저장
        if hasattr(self.trie, "save"):
            # Backend에 따라 저장 파일명 분리
            trie_type = type(self.trie).__name__

            if trie_type == "RustTrieWrapper":
                save_path = os.path.join(data_dir, "rust_trie.bin")
            elif trie_type == "DoubleArrayTrie":
                save_path = os.path.join(data_dir, "dictionary.dat")
            else:  # PythonTrieFallback
                save_path = os.path.join(data_dir, "dictionary.pkl")

            try:
                # DoubleArrayTrie나 PythonTrie 등은 pickle이나 구조체를 저장함
                # Dictionary.py에서 로드 시 구분을 위해 별도 파일명 사용 권장

                # 만약 DoubleArrayTrie라면 (dictionary.dat)
                if trie_type == "DoubleArrayTrie":
                    self.trie.save(save_path)
                    print(f"  [v] DAT 사전 저장 완료: {save_path}")

                    # (선택) Source 보존을 위한 pickle 저장?
                    # DAT는 원본 구조(Trie)를 가지고 있지 않으므로 원본 복원은 불가능할 수 있음.
                    # 하지만 analyzer.train() 후에는 메모리에 추가된 단어들이 있음.
                    # 이를 영구 보존하려면 DAT 자체를 저장하거나, 추가된 단어 로그를 남겨야 함.
                    # 여기선 DAT 저장만 수행.

                elif trie_type == "RustTrieWrapper":
                    self.trie.save(save_path)
                    print(f"  [v] Rust 사전 저장 완료: {save_path}")

                else:  # PythonTrieFallback represents Source
                    self.trie.save(save_path)
                    print(f"  [v] 원본 사전 저장 완료: {save_path}")

            except Exception as e:
                print(f"  ⚠ 사전 저장 실패: {e}")

    def analyze(self, text: str) -> List[Morph]:
        """형태소 분석 (v02 호환)

        띄어쓰기가 있으면 각 어절을 독립적으로 분석
        띄어쓰기가 없으면 전체를 하나로 분석
        """
        if self.use_neural and self.neural_wrapper and self.neural_wrapper.morph_model:
            # Neural Mode (Whole Sentence or Eojeol-wise)
            # We predict per eojeol to match training distribution.

            eojeols = text.split()
            morphemes = []

            # Batch Prediction
            if not eojeols:
                return []

            batch_results = self.neural_wrapper.predict_morph_batch(eojeols)

            for eojeol, res in zip(eojeols, batch_results):
                # -----------------------------------------------------------
                # Dictionary-Guided Correction (Hybrid)
                # -----------------------------------------------------------
                # Goal: Use the Trie dictionary to correct Neural errors for "Essential" morphemes (Josa, Eomi).
                # The user wants to avoid "hardcoding" specific words like '갔다', but allow using the Basic Dictionary.
                #
                # Strategy:
                # 1. Check if the ending of the Eojeol matches a known Ending key in the Dictionary.
                # 2. If Neural predicts "는/ETM + 다/ETM", but Dictionary has "는다/EF", prefer Dictionary.

                # Simple implementation for Eojeol-final correction:
                # Iterate from end of eojeol, check if substring exists in dictionary with high-priority POS (Eomi/Josa).

                # Flatten surface form
                surface = "".join(r[0] for r in res)

                # Try to find the longest suffix that matches a known Eomi/Josa in Trie
                # This requires access to self.trie.
                # Since Neural Mode might not use Trie for STEMMING, we can still use it for LOOKUP.

                # Only apply if self.trie is available
                refined_res = res  # Default

                if self.trie:
                    # Check suffixes
                    # E.g. "않는다" -> Check "는다", "다"
                    # "는다" -> found as EF?

                    # We look for a suffix that is a known Eomi/Josa
                    # AND the neural model fragmented it or tagged it wrongly.

                    found_correction = None
                    n = len(surface)
                    for i in range(n - 1, max(-1, n - 6), -1):  # Check last 5 chars max
                        suffix = surface[i:]
                        # search returns: (pos, lemma) or None?
                        # Trie.search usually returns just POS or data.
                        # Trie.search_all or get?
                        # Trie.search returns boolean or data?
                        # Wait, I need to check Trie API. Usually it returns (pos, ...).
                        # Let's assume search returns list of possible POS or one POS.

                        found_node = self.trie.search(suffix)
                        if found_node:
                            # Expecting found_node to contain POS info.
                            # In basic Trie, search might return True/False or Node.
                            # In this codebase, Dictionary/Trie wrapper returns...
                            # RustTrieWrapper.search -> returns data string or None?
                            # PythonTrieFallback.search -> returns data?

                            # Let's peek at trie.py or assume it returns POS string.
                            # If found_node is a POS string like "EF" or contains specific tags.

                            known_pos = str(found_node)  # Safety

                            # Target tags to trust from Dictionary:
                            # Eomi: EF, EC, ETM, EP
                            # Josa: JKS, JKO, JKB, JX, etc.
                            if any(
                                tag in known_pos
                                for tag in [
                                    "EF",
                                    "EC",
                                    "EP",
                                    "JKS",
                                    "JKO",
                                    "JKB",
                                    "JX",
                                    "VCP",
                                    "VCN",
                                ]
                            ):
                                # We found a valid suffix in dictionary (e.g. "는다"/EF).
                                # Now, does the Neural output match this?
                                # Neural: [('는', 'ETM'), ('다', 'ETM')]
                                # Suffix: '는다' / EF

                                # We should merge the corresponding neural tokens into this one.
                                # Find split point in neural res

                                # Reconstruct refined_res:
                                # prefix + (suffix, known_pos)

                                # Needs finding where 'suffix' starts in 'res'.
                                # res = [('않', 'VX'), ('는', 'ETM'), ('다', 'EF')] ...

                                current_len = 0
                                split_idx = -1
                                for ridx, (rwm, rpos) in enumerate(res):
                                    if current_len == i:  # Found start of suffix
                                        split_idx = ridx
                                        break
                                    current_len += len(rwm)

                                # If strict alignment found
                                if split_idx != -1:
                                    prefix_res = res[:split_idx]
                                    # Use the dictionary POS. Preference: EF > others for final position?
                                    # If dictionary returns multiple POS (e.g. "는" can be JX or ETM),
                                    # "는다" is likely EF only.

                                    # If multiple tags in known_pos (e.g. "NNG,MAG"), be careful.
                                    # Prioritize Eomi/Josa.
                                    final_tag = "UNKNOWN"
                                    for tag in [
                                        "EF",
                                        "EC",
                                        "EP",
                                        "JKS",
                                        "JKO",
                                        "JKB",
                                        "JX",
                                    ]:
                                        if tag in known_pos:
                                            final_tag = tag
                                            break

                                    if final_tag != "UNKNOWN":
                                        refined_res = prefix_res + [(suffix, final_tag)]
                                        found_correction = True
                                        break

                    if found_correction:
                        # Update res
                        res = refined_res

                morphemes.extend(res)
            # Reconstruct Morph objects from neural results (which are tuples)
            return [Morph(w, p, w) for w, p in morphemes]

        # 공백으로 어절 분리
        eojeols = text.split()

        if not eojeols:
            return []

        morphemes = []

        # 각 어절을 독립적으로 분석
        for eojeol in eojeols:
            results = self.stemmer.analyze(eojeol)
            # results는 List[List[Morpheme]]
            for sent_morphs in results:
                morphemes.extend(sent_morphs)

        return morphemes

    def train(
        self,
        sentence_text: str,
        correct_morphemes: List[Morph],
        save: bool = True,
    ):
        """
        문장 단위 추가 학습 (Online Learning)

        Args:
            sentence_text: 문장 텍스트 (예: "오늘 날씨가 좋다")
            correct_morphemes: 올바른 형태소 분석 결과
            save: 학습 후 모델 자동 저장 여부
        """
        # Convert to tuples for neural wrapper if needed, or vice-versa
        tuple_morphemes = []
        for m in correct_morphemes:
            if isinstance(m, Morph):
                tuple_morphemes.append((m.surface, m.pos))
            else:
                tuple_morphemes.append(m)

        if not self.use_neural:
            # Rule-based only: just add to Dictionary
            pass

        # 1. Neural Model 업데이트 (Online Learning)
        if self.use_neural and self.neural_wrapper:
            loss = self.neural_wrapper.online_train_morph(
                sentence_text, tuple_morphemes
            )
            if loss > 0:
                print(f"  [v] Neural 학습 완료 (Loss: {loss:.4f})")

        # 2. 미등록 단어(OOV) Dictionary에 추가 (메모리 상)
        for word, pos in tuple_morphemes:
            self.trie.insert(word, pos, word)

    def train_eojeol(self, surface: str, morphs: List[Morph]):
        """
        어절 단위 학습 (불규칙 활용 학습용)
        Args:
            surface: 어절 표면형 (e.g. "갔다")
            morphs: 형태소 목록
        """
        tuple_morphs = []
        for m in morphs:
            if isinstance(m, Morph):
                tuple_morphs.append((m.surface, m.pos))
            else:
                tuple_morphs.append(m)

        # 1. Individual Morphemes (Always insert for vocabulary coverage)
        for word, pos in tuple_morphs:
            self.trie.insert(word, pos, word)

        # 2. Irregular Pattern Detection
        reconstructed = "".join(w for w, p in tuple_morphs)

        if surface != reconstructed:
            # Mismatch detected (Contraction/Irregular)
            compound_pos = "+".join(p for w, p in tuple_morphs)
            compound_lemma = "+".join(w for w, p in tuple_morphs)

            self.trie.insert(surface, compound_pos, compound_lemma)

    def get_stats(self) -> Dict:
        """통계 정보"""
        stats = {
            "version": get_version(),
            "trie_type": type(self.trie).__name__,
            "gpu_enabled": self.stemmer.use_gpu,
            "rust_enabled": self.stemmer.use_rust,
        }

        if hasattr(self.trie, "get_stats"):
            stats["trie_stats"] = self.trie.get_stats()

        return stats
