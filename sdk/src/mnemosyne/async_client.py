"""
Async Mnemosyne API Client

Asynchronous version of the Mnemosyne client using httpx.AsyncClient
"""

import asyncio
import os
from typing import Optional, List, Dict, Any
from uuid import UUID

import httpx

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


class AsyncMnemosyneClient:
    """
    Async version of Mnemosyne client for use with async code.
    
    Example:
        >>> async with AsyncMnemosyneClient(api_key="your-key") as client:
        ...     result = await client.store("I love pizza")
        ...     memories = await client.retrieve("food preferences")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        self.api_key = api_key or os.getenv("MNEMOSYNE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Provide api_key parameter or set MNEMOSYNE_API_KEY environment variable."
            )
        
        self.base_url = (base_url or os.getenv("MNEMOSYNE_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-API-Key": self.api_key,
                "Accept": "application/json",
                "User-Agent": f"mnemosyne-python/0.1.0",
            },
            timeout=timeout,
            limits=limits,
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client connection"""
        await self._client.aclose()
    
    async def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> httpx.Response:
        """Make request with exponential backoff retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
                
                if response.status_code < 500 and response.status_code != 429:
                    return response
                    
                if attempt == self.max_retries:
                    return response
                    
                backoff = self.backoff_factor * (2 ** attempt)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", backoff))
                    await asyncio.sleep(retry_after)
                else:
                    await asyncio.sleep(backoff)
                    
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                if attempt == self.max_retries:
                    raise ServerError(f"Request failed after {self.max_retries} retries: {str(e)}")
                await asyncio.sleep(self.backoff_factor * (2 ** attempt))
        
        return response

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions"""
        try:
            data = response.json() if response.content else {}
        except Exception:
            data = {}
        
        if response.status_code in (200, 201, 202):
            return data
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
    
    async def store(
        self,
        content: str,
        memory_type: Optional[MemoryType] = None,
        metadata: Optional[Dict[str, Any]] = None,
        async_processing: bool = True,
    ) -> StoreResponse:
        """Async version of store()"""
        request = StoreRequest(
            content=content,
            memory_type=memory_type or MemoryType.FACT,
            metadata=metadata,
            async_processing=async_processing,
        )
        
        response = await self._request_with_retry(
            "POST",
            "/v1/memories/store",
            json=request.model_dump(exclude_none=True),
        )
        
        data = await self._handle_response(response)
        return StoreResponse(**data)
    
    async def store_turns(
        self,
        turns: List[Dict[str, str]],
        memory_type: Optional[MemoryType] = None,
        async_processing: bool = True,
    ) -> StoreResponse:
        """Async version of store_turns()"""
        content_parts = []
        for turn in turns:
            role = turn.get("role", "unknown")
            text = turn.get("content", "")
            content_parts.append(f"{role}: {text}")
        
        combined_content = "\n".join(content_parts)
        metadata = {"conversation_turns": turns}
        
        return await self.store(
            content=combined_content,
            memory_type=memory_type,
            metadata=metadata,
            async_processing=async_processing,
        )
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_confidence: float = 0.5,
    ) -> List[Memory]:
        """Async version of retrieve()"""
        response = await self._request_with_retry(
            "POST",
            "/v1/memories/retrieve",
            json={
                "query": query,
                "top_k": top_k,
                "memory_type": memory_type.value if memory_type else None,
                "min_confidence": min_confidence,
            },
        )
        
        data = await self._handle_response(response)
        search_result = MemorySearchResult(**data)
        return search_result.memories
    
    async def retrieve_with_scores(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_confidence: float = 0.5,
    ) -> MemorySearchResult:
        """Async version of retrieve_with_scores()"""
        response = await self._request_with_retry(
            "POST",
            "/v1/memories/retrieve",
            json={
                "query": query,
                "top_k": top_k,
                "memory_type": memory_type.value if memory_type else None,
                "min_confidence": min_confidence,
            },
        )
        
        data = await self._handle_response(response)
        return MemorySearchResult(**data)
    
    async def list_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Memory]:
        """Async version of list_memories()"""
        params = {"limit": limit, "offset": offset}
        if memory_type:
            params["memory_type"] = memory_type.value
        
        response = await self._request_with_retry("GET", "/v1/memories/list", params=params)
        data = await self._handle_response(response)
        
        return [Memory(**item) for item in data]
    
    async def get_memory(self, memory_id: UUID) -> Memory:
        """Async version of get_memory()"""
        response = await self._request_with_retry("GET", f"/v1/memories/{memory_id}")
        data = await self._handle_response(response)
        return Memory(**data)
    
    async def delete_memory(self, memory_id: UUID) -> bool:
        """Async version of delete_memory()"""
        response = await self._request_with_retry("DELETE", f"/v1/memories/{memory_id}")
        await self._handle_response(response)
        return True
    
    async def get_job_status(self, job_id: UUID) -> JobStatus:
        """Async version of get_job_status()"""
        response = await self._request_with_retry("GET", f"/v1/memories/job/{job_id}/status")
        data = await self._handle_response(response)
        return JobStatus(**data)
    
    async def wait_for_job(
        self,
        job_id: UUID,
        timeout: float = 60.0,
        poll_interval: float = 1.0,
    ) -> JobStatus:
        """Async version of wait_for_job()"""
        import asyncio
        
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            status = await self.get_job_status(job_id)
            
            if status.status in ("completed", "failed"):
                return status
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
    
    async def health_check(self) -> Dict[str, str]:
        """Async version of health_check()"""
        response = await self._request_with_retry("GET", "/health")
        return await self._handle_response(response)
    
    async def ping(self) -> bool:
        """Async version of ping()"""
        try:
            result = await self.health_check()
            return result.get("status") == "healthy"
        except Exception:
            return False
