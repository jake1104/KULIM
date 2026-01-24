from importlib.metadata import version, PackageNotFoundError

from .hangul import (
    is_hangul,
    decompose,
    decompose_korean,
    compose,
    compose_korean,
    has_jongsung,
    CHOSUNG,
    JUNGSUNG,
    JONGSUNG,
)

try:
    __version__ = version("hangul")
except PackageNotFoundError:
    __version__ = "0.1.0"
