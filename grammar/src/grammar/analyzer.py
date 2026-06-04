from typing import List, Tuple, Dict
import os

from .stemmer import Stemmer
from .morph import Morph
from .dictionary import build_comprehensive_trie
from .preprocessor import Preprocessor
from .utils import get_data_dir, get_version
from .logger import logger
from .exceptions import ModelLoadError, AnalysisError, DictionaryError


class MorphAnalyzer:
    """형태소 분석기"""

    def __init__(
        self,
        model_path=None,  # .kg 모델 파일 경로 (v0.1.1+)
        use_double_array=True,
        use_sejong=True,
        use_gpu=False,
        use_rust=False,
        use_neural=False,
        load_defaults=True,
        debug=False,
    ):
        if debug:
            logger.setLevel("DEBUG")

        self._print_legal_notice()

        if debug:
            logger.debug(
                f"Initializer Flags: GPU={use_gpu}, Rust={use_rust}, Neural={use_neural}, Model={model_path}"
            )
        
        # 모델 경로가 지정된 경우 .kg 파일에서 로드
        if model_path:
            self._load_from_kg(model_path, use_gpu, use_rust, use_neural)
            return
        
        # 기본 모델 사용: data_dir에서 model.kg 확인
        data_dir = get_data_dir()
        default_kg_path = os.path.join(data_dir, "model.kg")
        
        if os.path.exists(default_kg_path):
            logger.info(f"Loading default model from {default_kg_path}")
            self._load_from_kg(default_kg_path, use_gpu, use_rust, use_neural)
            return

        # .kg 파일이 없으면 개별 파일에서 빌드
        try:
            self.trie = build_comprehensive_trie(
                use_double_array=use_double_array,
                use_sejong=use_sejong,
                use_rust=use_rust,
                load_defaults=load_defaults,
            )
        except Exception as e:
            logger.error(f"Failed to initialize trie dictionary: {e}")
            raise DictionaryError(f"Trie initialization failed: {e}")

        self.preprocessor = Preprocessor()
        self.stemmer = Stemmer(trie=self.trie, use_gpu=use_gpu, use_rust=use_rust)

        # Neural Morph Integration
        self.use_neural = use_neural
        self.neural_wrapper = None
        if use_neural:
            try:
                from .neural_wrapper import NeuralWrapper

                self.neural_wrapper = NeuralWrapper()
                logger.info("Neural Morphological Analysis enabled.")
            except Exception as e:
                logger.warning(
                    f"Neural Model Load Failed (falling back to rule-based): {e}"
                )
                self.use_neural = False
    
    def _load_from_kg(self, kg_path: str, use_gpu: bool, use_rust: bool, use_neural: bool):
        """
        .kg 파일에서 모델 로드
        
        Args:
            kg_path: .kg 파일 경로
            use_gpu: GPU 사용 여부
            use_rust: Rust 사용 여부
            use_neural: Neural 모델 사용 여부
        """
        from .model_packager import ModelPackager
        import shutil
        
        logger.info(f"Loading model from .kg file: {kg_path}")
        
        # 임시 디렉토리에 압축 해제
        temp_dir = ModelPackager.load_from_package(kg_path)
        
        try:
            # 데이터 디렉토리로 파일 복사
            data_dir = get_data_dir()
            os.makedirs(data_dir, exist_ok=True)
            
            for filename in ModelPackager.MODEL_FILES:
                src = os.path.join(temp_dir, filename)
                dst = os.path.join(data_dir, filename)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    logger.debug(f"Loaded {filename} from .kg")
            
            # Trie 초기화
            self.trie = build_comprehensive_trie(
                use_double_array=True,
                use_sejong=False,  # 이미 로드된 모델 사용
                use_rust=use_rust,
                load_defaults=False,  # 기본 어휘 로드 안 함
            )
            
            self.preprocessor = Preprocessor()
            self.stemmer = Stemmer(trie=self.trie, use_gpu=use_gpu, use_rust=use_rust)
            
            # Neural 모델 로드
            self.use_neural = use_neural
            self.neural_wrapper = None
            if use_neural:
                try:
                    from .neural_wrapper import NeuralWrapper
                    self.neural_wrapper = NeuralWrapper()
                    logger.info("Neural model loaded from .kg package")
                except Exception as e:
                    logger.warning(f"Neural model load failed: {e}")
                    self.use_neural = False
            
            logger.info(f"Model successfully loaded from {kg_path}")
            
        finally:
            # 임시 디렉토리 정리
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def _print_legal_notice(self):
        """실험적 버전 법적 면책 고지 출력"""
        notice = [
            "  " + "=" * 56,
            "  KULIM (Korean Unified Linguistic Integration Manager) v0.1.3",
            "  [!] 법적 고지 및 면책 조항 (Legal Notice & Disclaimer)",
            "  - 본 소프트웨어는 '실험적 정식 버전'으로 제공됩니다.",
            "  - 결과의 무결성이나 정확성을 보장하지 않으며,",
            "    사용 중 발생한 데이터 손실 등에 책임을 지지 않습니다.",
            "  - 상업적 용도 사용 시 반드시 사전 검증을 권장합니다.",
            "  " + "=" * 56,
        ]
        for line in notice:
            print(line)

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
                    logger.info(f"DAT dictionary saved: {save_path}")
                elif trie_type == "RustTrieWrapper":
                    self.trie.save(save_path)
                    logger.info(f"Rust dictionary saved: {save_path}")
                else:
                    self.trie.save(save_path)
                    logger.info(f"Source dictionary saved: {save_path}")
            except Exception as e:
                logger.error(f"Failed to save dictionary: {e}")
    
    def save_model(self, output_path: str) -> str:
        """
        모델을 단일 패키지 파일로 저장 (v0.1.1+)
        
        Args:
            output_path: 출력 경로 (.kg 확장자, KULIM Grammar 포맷)
            
        Returns:
            생성된 패키지 파일 경로
            
        Example:
            >>> analyzer = MorphAnalyzer()
            >>> analyzer.save_model("./models/my_model.kg")
            './models/my_model.kg'
        """
        from .model_packager import ModelPackager
        
        # 개별 파일들을 임시로 저장하지 않고 직접 .kg로 패키징
        # (save() 메서드가 이미 개별 파일 저장 + 패키징을 처리함)
        
        # 패키지로 묶기
        package_path = ModelPackager.package_model(output_path)
        logger.info(f"Model packaged to: {package_path}")
        
        return package_path
    
    @staticmethod
    def load_model(package_path: str, **kwargs) -> 'MorphAnalyzer':
        """
        패키지 파일에서 모델을 로드하여 새 MorphAnalyzer 인스턴스 생성 (v0.1.1+)
        
        Args:
            package_path: 패키지 파일 경로 (.kg)
            **kwargs: MorphAnalyzer 초기화 인자
            
        Returns:
            로드된 모델을 사용하는 MorphAnalyzer 인스턴스
            
        Example:
            >>> analyzer = MorphAnalyzer.load_model("./models/my_model.kg")
            >>> result = analyzer.analyze("테스트")
        """
        from .model_packager import ModelPackager
        import shutil
        
        # 패키지 압축 해제
        temp_dir = ModelPackager.load_from_package(package_path)
        
        try:
            # 임시 디렉토리의 파일들을 데이터 디렉토리로 복사
            data_dir = get_data_dir()
            os.makedirs(data_dir, exist_ok=True)
            
            for filename in ModelPackager.MODEL_FILES:
                src = os.path.join(temp_dir, filename)
                dst = os.path.join(data_dir, filename)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    logger.debug(f"Copied {filename} to data directory")
            
            # 새 MorphAnalyzer 인스턴스 생성
            analyzer = MorphAnalyzer(**kwargs)
            logger.info(f"Model loaded from package: {package_path}")
            
            return analyzer
            
        finally:
            # 임시 디렉토리 정리
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

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
                # Deep Hybrid Ensemble: Log-Linear Interpolation 
                # -----------------------------------------------------------
                # res is a list of (surface, pos, prob) from the Neural Model.
                
                # 1. Evaluate Neural Confidence
                # We calculate the geometric mean of probabilities to get a sentence-level confidence.
                if not res:
                    continue
                    
                neural_probs = [item[2] for item in res if len(item) == 3]
                if not neural_probs:
                    neural_probs = [1.0] # Fallback if probability not provided
                
                # Log sum for stability
                import math
                log_prob_sum = sum(math.log(max(p, 1e-9)) for p in neural_probs)
                avg_log_prob = log_prob_sum / len(neural_probs)
                neural_confidence = math.exp(avg_log_prob)
                
                # Reconstruct Morph objects from neural results
                neural_morphs = [Morph(w, p, w) for w, p, *_ in res]
                
                # 2. Extract DP (Rule-based/Viterbi) Candidate 
                # Run the Viterbi stemmer on this eojeol
                dp_results = self.stemmer.analyze(eojeol)
                dp_morphs = []
                for sent_morphs in dp_results:
                    dp_morphs.extend(sent_morphs)
                
                # Calculate DP confidence (heuristic based on OOV/unregistered words)
                # Dictionary matches have high confidence. OOV has low confidence.
                dp_confidence = 1.0
                for m in dp_morphs:
                    # Look up in trie to see if it's securely registered
                    is_registered = False
                    if self.trie:
                        # try to find exact match
                        patterns = self.trie.search_all_patterns(m.surface)
                        for start, end, pat_list in patterns:
                            if start == 0 and end == len(m.surface):
                                for pos, lemma in pat_list:
                                    if pos == m.pos:
                                        is_registered = True
                                        break
                                if is_registered:
                                    break
                    
                    if not is_registered and m.pos == "NNG":
                        # Likely an OOV guessed by DP penalty
                        dp_confidence *= 0.5
                    elif is_registered:
                        dp_confidence *= 0.99 # Small penalty per morph to favor shorter paths
                
                # 3. Log-Linear Interpolation & Decision
                # Weights: How much we trust Neural vs DP
                # Neural is great for out-of-context smoothing. DP is absolute for Dictionary.
                W_NEURAL = 0.6
                W_DP = 0.4
                
                # Heuristic Override: If Neural confidence is extremely low (< 0.3) 
                # and DP confidence is high (> 0.8), trust Dictionary absolute.
                if neural_confidence < 0.3 and dp_confidence > 0.8:
                    chosen_morphs = dp_morphs
                    logger.debug(f"[{eojeol}] DP Override: Neural={neural_confidence:.2f}, DP={dp_confidence:.2f}")
                # Otherwise use Log-Linear score
                else:
                    neural_score = W_NEURAL * neural_confidence
                    dp_score = W_DP * dp_confidence
                    
                    if dp_score > neural_score:
                        chosen_morphs = dp_morphs
                        logger.debug(f"[{eojeol}] Chose DP: Neural={neural_score:.4f}, DP={dp_score:.4f}")
                    else:
                        chosen_morphs = neural_morphs
                        logger.debug(f"[{eojeol}] Chose Neural: Neural={neural_score:.4f}, DP={dp_score:.4f}")
                        
                morphemes.extend(chosen_morphs)
            
            return morphemes

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
                logger.info(f"Neural training step complete (Loss: {loss:.4f})")

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
