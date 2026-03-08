"""
Mnemosyne API Client

Main client for interacting with Mnemosyne Memory API
"""

import os
import time
from typing import Optional, List, Dict, Any
from uuid import UUID

import httpx
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    MnemosyneError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)
from .memory import Memory, MemorySearchResult, StoreRequest, StoreResponse, JobStatus, MemoryType


DEFAULT_BASE_URL = "https://api.mnemosyne.dev"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1.0


class MnemosyneClient:
    """
    Official Python client for Mnemosyne AI Memory Layer.
    
    Example:
        >>> from mnemosyne import MnemosyneClient
        >>> client = MnemosyneClient(api_key="your-api-key")
        >>> 
        >>> # Store a memory
        >>> result = client.store("User loves Italian food but is gluten-free")
        >>> 
        >>> # Retrieve memories
        >>> memories = client.retrieve("What are user's dietary restrictions?")
        >>> for memory in memories:
        ...     print(memory.content)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Initialize Mnemosyne client.
        
        Args:
            api_key: Mnemosyne API key. If not provided, reads from MNEMOSYNE_API_KEY env var.
            base_url: API base URL. Defaults to https://api.mnemosyne.dev
            timeout: Request timeout in seconds. Default 30s.
            max_retries: Maximum number of retries for failed requests. Default 3.
            backoff_factor: Exponential backoff factor. Default 1.0.
        
        Raises:
            AuthenticationError: If no API key is provided or found.
        """
        self.api_key = api_key or os.getenv("MNEMOSYNE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Provide api_key parameter or set MNEMOSYNE_API_KEY environment variable."
            )
        
        self.base_url = (base_url or os.getenv("MNEMOSYNE_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Initialize HTTP client with connection pooling
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-API-Key": self.api_key,
                "Accept": "application/json",
                "User-Agent": f"mnemosyne-python/0.1.0",
            },
            timeout=timeout,
            limits=limits,
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client connection"""
        self._client.close()
    
    def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> httpx.Response:
        """Make request with exponential backoff retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(method, path, **kwargs)
                
                # Don't retry on client errors (4xx) except rate limit (429)
                if response.status_code < 500 and response.status_code != 429:
                    return response
                    
                # Don't retry if not the last attempt
                if attempt == self.max_retries:
                    return response
                    
                # Calculate backoff time
                backoff = self.backoff_factor * (2 ** attempt)
                if response.status_code == 429:
                    # Respect Retry-After header for rate limits
                    retry_after = int(response.headers.get("Retry-After", backoff))
                    time.sleep(retry_after)
                else:
                    time.sleep(backoff)
                    
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt == self.max_retries:
                    raise ServerError(f"Request failed after {self.max_retries} retries: {str(e)}")
                time.sleep(self.backoff_factor * (2 ** attempt))
        
        return response

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions"""
        try:
            data = response.json() if response.content else {}
        except Exception:
            data = {}
        
        if response.status_code == 200 or response.status_code == 201:
            return data
        elif response.status_code == 202:
            return data  # Accepted for async processing
        elif response.status_code == 401:
            raise AuthenticationError(data.get("detail", "Authentication failed"))
        elif response.status_code == 404:
            raise NotFoundError(data.get("detail", "Resource not found"))
        elif response.status_code == 422:
            raise ValidationError(
                data.get("detail", "Validation error"),
                errors=data.get("errors", {}),
            )
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                data.get("detail", "Rate limit exceeded"),
                retry_after=retry_after,
            )
        elif response.status_code >= 500:
            raise ServerError(
                data.get("detail", "Server error"),
                status_code=response.status_code,
            )
        else:
            raise MnemosyneError(
                data.get("detail", f"API error: {response.status_code}"),
                status_code=response.status_code,
                response_data=data,
            )
    
    def store(
        self,
        content: str,
        memory_type: Optional[MemoryType] = None,
        metadata: Optional[Dict[str, Any]] = None,
        async_processing: bool = True,
    ) -> StoreResponse:
        """
        Store a memory for the user.
        
        Args:
            content: The content to store (conversation, fact, preference, etc.)
            memory_type: Type of memory (preference, fact, entity, etc.)
            metadata: Optional metadata to attach
            async_processing: If True, process asynchronously (default). 
                             If False, wait for distillation.
        
        Returns:
            StoreResponse with job_id (async) or memory_ids (sync)
        
        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
            ValidationError: If content is invalid
        
        Example:
            >>> result = client.store("I'm gluten-free and love Italian food")
            >>> print(result.status)  # "accepted" or "completed"
        """
        request = StoreRequest(
            content=content,
            memory_type=memory_type or MemoryType.FACT,
            metadata=metadata,
            async_processing=async_processing,
        )
        
        response = self._request_with_retry(
            "POST",
            "/v1/memories/store",
            json=request.model_dump(exclude_none=True),
        )
        
        data = self._handle_response(response)
        return StoreResponse(**data)
    
    def store_turns(
        self,
        turns: List[Dict[str, str]],
        memory_type: Optional[MemoryType] = None,
        async_processing: bool = True,
    ) -> StoreResponse:
        """
        Store a conversation with multiple turns.
        
        Args:
            turns: List of {"role": "user"|"assistant", "content": "..."}
            memory_type: Type of memory to extract
            async_processing: Process asynchronously (default True)
        
        Returns:
            StoreResponse
        
        Example:
            >>> turns = [
            ...     {"role": "user", "content": "I need a gluten-free restaurant"},
            ...     {"role": "assistant", "content": "I know a great Italian place..."},
            ... ]
            >>> result = client.store_turns(turns)
        """
        # Combine turns into single content with structure
        content_parts = []
        for turn in turns:
            role = turn.get("role", "unknown")
            text = turn.get("content", "")
            content_parts.append(f"{role}: {text}")
        
        combined_content = "\n".join(content_parts)
        metadata = {"conversation_turns": turns}
        
        return self.store(
            content=combined_content,
            memory_type=memory_type,
            metadata=metadata,
            async_processing=async_processing,
        )
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_confidence: float = 0.5,
    ) -> List[Memory]:
        """
        Retrieve relevant memories based on a query.
        
        Uses semantic search with temporal weighting to return
        the most relevant, recent memories first.
        
        Args:
            query: Natural language query
            top_k: Number of results to return (1-20, default 5)
            memory_type: Filter by memory type
            min_confidence: Minimum confidence score (0.0-1.0)
        
        Returns:
            List of Memory objects
        
        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
        
        Example:
            >>> memories = client.retrieve("What food does the user like?")
            >>> for m in memories:
            ...     print(f"{m.content} (confidence: {m.confidence})")
        """
        response = self._request_with_retry(
            "POST",
            "/v1/memories/retrieve",
            json={
                "query": query,
                "top_k": top_k,
                "memory_type": memory_type.value if memory_type else None,
                "min_confidence": min_confidence,
            },
        )
        
        data = self._handle_response(response)
        search_result = MemorySearchResult(**data)
        return search_result.memories
    
    def retrieve_with_scores(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_confidence: float = 0.5,
    ) -> MemorySearchResult:
        """
        Retrieve memories with full search result metadata.
        
        Same as retrieve() but returns full MemorySearchResult
        including search_time_ms and total_found.
        """
        response = self._request_with_retry(
            "POST",
            "/v1/memories/retrieve",
            json={
                "query": query,
                "top_k": top_k,
                "memory_type": memory_type.value if memory_type else None,
                "min_confidence": min_confidence,
            },
        )
        
        data = self._handle_response(response)
        return MemorySearchResult(**data)
    
    def list_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Memory]:
        """
        List all memories with optional filtering.
        
        Args:
            memory_type: Filter by type
            limit: Max results (1-100, default 20)
            offset: Pagination offset
        
        Returns:
            List of Memory objects
        """
        params = {"limit": limit, "offset": offset}
        if memory_type:
            params["memory_type"] = memory_type.value
        
        response = self._request_with_retry("GET", "/v1/memories/list", params=params)
        data = self._handle_response(response)
        
        return [Memory(**item) for item in data]
    
    def get_memory(self, memory_id: UUID) -> Memory:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: UUID of the memory
        
        Returns:
            Memory object
        
        Raises:
            NotFoundError: If memory doesn't exist
        """
        response = self._request_with_retry("GET", f"/v1/memories/{memory_id}")
        data = self._handle_response(response)
        return Memory(**data)
    
    def delete_memory(self, memory_id: UUID) -> bool:
        """
        Delete a specific memory.
        
        Args:
            memory_id: UUID of the memory to delete
        
        Returns:
            True if deleted successfully
        
        Raises:
            NotFoundError: If memory doesn't exist
        """
        response = self._request_with_retry("DELETE", f"/v1/memories/{memory_id}")
        self._handle_response(response)
        return True
    
    def get_job_status(self, job_id: UUID) -> JobStatus:
        """
        Check status of an async distillation job.
        
        Args:
            job_id: UUID of the job
        
        Returns:
            JobStatus with current state and results
        """
        response = self._request_with_retry("GET", f"/v1/memories/job/{job_id}/status")
        data = self._handle_response(response)
        return JobStatus(**data)
    
    def wait_for_job(
        self,
        job_id: UUID,
        timeout: float = 60.0,
        poll_interval: float = 1.0,
    ) -> JobStatus:
        """
        Poll job status until completion or timeout.
        
        Args:
            job_id: UUID of the job to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Seconds between status checks
        
        Returns:
            JobStatus (completed or failed)
        
        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            if status.status in ("completed", "failed"):
                return status
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
    
    def health_check(self) -> Dict[str, str]:
        """
        Check API health status.
        
        Returns:
            Dict with status information
        """
        response = self._request_with_retry("GET", "/health")
        return self._handle_response(response)
    
    def ping(self) -> bool:
        """
        Quick connectivity check.
        
        Returns:
            True if API is reachable and healthy
        """
        try:
            result = self.health_check()
            return result.get("status") == "healthy"
        except Exception:
            return False
