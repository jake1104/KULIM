from importlib.metadata import version, PackageNotFoundError

from .hangul import is_hangul, decompose, decompose_korean, compose, compose_korean, has_jongsung

try:
    __version__ = version("hangul")
except PackageNotFoundError:
    __version__ = "0.0.1"
