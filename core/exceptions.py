class FrameworkError(Exception):
    """Base exception for framework-specific failures."""


class DataFileFormatError(FrameworkError):
    """Raised when an Excel file is missing required structure."""


class MissingCaseDataError(FrameworkError):
    """Raised when a data-driven case cannot locate its expected dataset."""


class UnsupportedBrowserError(FrameworkError):
    """Raised when the requested browser is not supported."""

