"""
Mnemosyne SDK Exceptions
"""

from typing import Optional, Dict, Any


class MnemosyneError(Exception):
    """Base exception for Mnemosyne SDK"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(MnemosyneError):
    """Raised when API key is invalid or missing"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(MnemosyneError):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NotFoundError(MnemosyneError):
    """Raised when resource is not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(MnemosyneError):
    """Raised when request validation fails"""
    
    def __init__(self, message: str = "Validation error", errors: Optional[Dict] = None):
        super().__init__(message, status_code=422)
        self.errors = errors or {}


class ServerError(MnemosyneError):
    """Raised when server returns 5xx error"""
    
    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__(message, status_code=status_code)
