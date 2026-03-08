"""
Redis cache service
"""

import json
from typing import Optional, Any
import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


class RedisCache:
    """Redis cache wrapper for Mnemosyne"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_POOL_SIZE,
            )
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def ping(self) -> bool:
        """Check Redis connectivity"""
        if not self._client:
            return False
        try:
            return await self._client.ping()
        except Exception:
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self._client:
            return None
        return await self._client.get(key)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Set value in cache"""
        if not self._client:
            return
        if expire:
            await self._client.setex(key, expire, value)
        else:
            await self._client.set(key, value)
    
    async def setex(self, key: str, seconds: int, value: str):
        """Set value with expiration"""
        if not self._client:
            return
        await self._client.setex(key, seconds, value)
    
    async def set_json(self, key: str, value: Any, expire: Optional[int] = None):
        """Set JSON value in cache"""
        await self.set(key, json.dumps(value), expire)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self._client:
            return
        await self._client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._client:
            return False
        return await self._client.exists(key) > 0
    
    # Memory-specific operations
    
    async def get_memory_cache(self, user_id: str, memory_id: str) -> Optional[dict]:
        """Get cached memory"""
        key = f"memory:{user_id}:{memory_id}"
        return await self.get_json(key)
    
    async def set_memory_cache(self, user_id: str, memory_id: str, data: dict, expire: int = 300):
        """Cache memory for quick retrieval"""
        key = f"memory:{user_id}:{memory_id}"
        await self.set_json(key, data, expire)
    
    async def invalidate_memory_cache(self, user_id: str, memory_id: str):
        """Invalidate memory cache"""
        key = f"memory:{user_id}:{memory_id}"
        await self.delete(key)
    
    async def get_search_cache(self, user_id: str, query_hash: str) -> Optional[list]:
        """Get cached search results"""
        key = f"search:{user_id}:{query_hash}"
        return await self.get_json(key)
    
    async def set_search_cache(self, user_id: str, query_hash: str, results: list, expire: int = 60):
        """Cache search results"""
        key = f"search:{user_id}:{query_hash}"
        await self.set_json(key, results, expire)
    
    # Rate limiting
    
    async def check_rate_limit(self, key: str, max_requests: int, window: int) -> tuple[bool, int]:
        """
        Check if request is within rate limit.
        Returns (allowed, remaining_requests)
        """
        if not self._client:
            return True, max_requests
        
        current = await self._client.get(key)
        
        if current is None:
            # First request in window
            await self._client.setex(key, window, 1)
            return True, max_requests - 1
        
        count = int(current)
        if count >= max_requests:
            return False, 0
        
        await self._client.incr(key)
        return True, max_requests - count - 1
