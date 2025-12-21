"""
KULIM Grammar
=====================
사전 구축, 데이터셋 학습, 형태소 분석기 API
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("grammar")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

# 1. 사전 구축 (Dictionary Builder)
from .dictionary import build_comprehensive_trie

# 2. HMM 모델 학습 (Dataset Training)
from .hmm_trainer import HMMTrainer

# 3. 형태소 분석기 (Morphological Analyzer)
from .analyzer import MorphAnalyzer

# 추가 유틸리티
from .stemmer import Stemmer
from .conjugation import ConjugationAnalyzer
from .irregular import IrregularConjugation
from .morph import (
    Morph,
    is_lexical_morph,
    is_functional_morph,
    is_free_morph,
    is_bound_morph,
)
from .syntax import SyntaxAnalyzer, SentenceComponent


# Public API
__all__ = [
    # 버전
    "__version__",
    # 1. 사전 구축
    "build_comprehensive_trie",
    # 2. 데이터셋 학습
    "HMMTrainer",
    # 3. 형태소 분석기
    "MorphAnalyzer",
    "Morph",
    "is_lexical_morph",
    "is_functional_morph",
    "is_free_morph",
    "is_bound_morph",
    # 추가 유틸리티
    "Stemmer",
    "ConjugationAnalyzer",
    "IrregularConjugation",
    "SyntaxAnalyzer",
    "SentenceComponent",
]


# GPU 모듈
try:
    import cupy as cp
    from .gpu import GPUBatchAnalyzer, get_gpu_info

    HAS_GPU = True
except ImportError:
    GPUBatchAnalyzer = None
    get_gpu_info = lambda: {"available": False, "message": "CuPy not installed"}
    HAS_GPU = False


# GPU 기능이 있으면 추가
if HAS_GPU:
    __all__.extend(
        [
            "GPUBatchAnalyzer",
            "get_gpu_info",
        ]
    )
