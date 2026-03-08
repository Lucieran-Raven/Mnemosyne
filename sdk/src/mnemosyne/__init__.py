"""
Mnemosyne Python SDK

The official Python client for Mnemosyne - AI Memory Layer
"""

__version__ = "0.1.0"

from .client import MnemosyneClient
from .async_client import AsyncMnemosyneClient
from .memory import Memory, MemoryType, MemorySearchResult, StoreResponse, JobStatus
from .exceptions import (
    MnemosyneError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)

__all__ = [
    "MnemosyneClient",
    "AsyncMnemosyneClient",
    "Memory",
    "MemoryType",
    "MemorySearchResult",
    "StoreResponse",
    "JobStatus",
    "MnemosyneError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
]
