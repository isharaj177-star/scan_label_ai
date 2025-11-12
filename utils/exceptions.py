"""
Custom exceptions for ScanLabel AI.
"""


class ScanLabelException(Exception):
    """Base exception for ScanLabel AI."""
    pass


class ModelLoadError(ScanLabelException):
    """Raised when model fails to load."""
    pass


class ProductNotFoundError(ScanLabelException):
    """Raised when product is not found in database."""
    pass


class InvalidBarcodeError(ScanLabelException):
    """Raised when barcode format is invalid."""
    pass


class InsufficientDataError(ScanLabelException):
    """Raised when product data is insufficient for analysis."""
    pass


class APIError(ScanLabelException):
    """Raised when external API call fails."""
    pass


class PredictionError(ScanLabelException):
    """Raised when model prediction fails."""
    pass








