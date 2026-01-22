class KulimError(Exception):
    """Base class for exceptions in this module."""

    pass


class ModelLoadError(KulimError):
    """Raised when a model file fails to load."""

    pass


class DictionaryError(KulimError):
    """Raised when dictionary operations fail."""

    pass


class AnalysisError(KulimError):
    """Raised when analysis fails."""

    pass


class RustExtensionError(KulimError):
    """Raised when Rust extension fails."""

    pass


class GpuError(KulimError):
    """Raised when GPU acceleration fails."""

    pass
