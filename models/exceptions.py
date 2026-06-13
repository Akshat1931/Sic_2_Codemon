"""
models/exceptions.py - Custom exception classes for DisasterOS validation errors.
Matches Section 15 of the PDF.
"""

class CoordinateError(ValueError):
    """Exception raised when latitude or longitude are outside valid ranges."""
    pass

class NodeNotFoundError(KeyError):
    """Exception raised when a location ID is not found in the disaster graph."""
    pass

class RoutingError(ValueError):
    """Exception raised when route planning is invalid (e.g. source == target or disconnected)."""
    pass
