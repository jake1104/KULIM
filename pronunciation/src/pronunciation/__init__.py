from importlib.metadata import version, PackageNotFoundError
from .engine import PronunciationEngine

try:
    __version__ = version("pronunciation")
except PackageNotFoundError:
    __version__ = "0.1.0"

_engine = PronunciationEngine()

def pronounce(text: str) -> str:
    """한글 문장을 표준 발음으로 변환합니다 (Professional Engine)."""
    return _engine.pronounce(text)

def pronounce_korean(text: str) -> str:
    """Alias for pronounce."""
    return pronounce(text)

__all__ = ["pronounce", "pronounce_korean", "PronunciationEngine"]
