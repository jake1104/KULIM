from importlib.metadata import version, PackageNotFoundError

from .hangul import *


try:
    __version__ = version("hangul")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
