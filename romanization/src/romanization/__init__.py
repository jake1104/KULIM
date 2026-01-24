from importlib.metadata import version, PackageNotFoundError

from .romanization import romanize, romanize_korean, romanize_pronunciation, romanize_standard

try:
    __version__ = version("romanization")
except PackageNotFoundError:
    __version__ = "0.0.1"
