"""
Authentication service - API key and JWT validation
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, Header, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.models import User
from app.core.config import get_settings
from app.services.redis_cache import RedisCache

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate user via API key (X-API-Key header) or Bearer token.
    Priority: API key for SDK usage, Bearer token for dashboard.
    """
    redis = RedisCache()
    await redis.connect()
    
    try:
        # Try API key first (preferred for programmatic access)
        if x_api_key:
            user = await authenticate_api_key(x_api_key, db, redis)
            if user:
                return user
        
        # Try Bearer token (for dashboard/Clerk)
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            user = await authenticate_jwt(token, db, redis)
            if user:
                return user
        
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    finally:
        await redis.disconnect()


async def authenticate_api_key(
    api_key: str,
    db: AsyncSession,
    redis: RedisCache,
) -> Optional[User]:
    """Authenticate user by API key with caching"""
    
    # Check cache first
    cache_key = f"api_key:{api_key}"
    cached_user_id = await redis.get(cache_key)
    
    if cached_user_id:
        # Get user by ID from cache
        query = select(User).where(User.id == UUID(cached_user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            return user
    
    # Cache miss - query database
    query = select(User).where(User.api_key == api_key)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user:
        # Cache for 5 minutes
        await redis.setex(cache_key, 300, str(user.id))
        return user
    
    return None


async def authenticate_jwt(
    token: str,
    db: AsyncSession,
    redis: RedisCache,
) -> Optional[User]:
    """Authenticate user by JWT token (Clerk)"""
    
    try:
        import requests
        
        # Verify token with Clerk
        response = requests.get(
            "https://api.clerk.dev/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        if response.status_code != 200:
            return None
        
        clerk_user = response.json()
        external_id = clerk_user.get("id")
        
        if not external_id:
            return None
        
        # Find or create user
        query = select(User).where(User.external_id == external_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                external_id=external_id,
                email=clerk_user.get("email_addresses", [{}])[0].get("email_address"),
            )
            db.add(user)
            await db.commit()
        
        return user
        
    except Exception:
        return None


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin privileges"""
    # TODO: Implement admin role check
    # For now, allow all authenticated users
    return current_user


# Internal API key for worker authentication
INTERNAL_API_KEY = settings.INTERNAL_API_KEY or "dev-internal-key"

async def get_internal_api_key(
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key"),
) -> str:
    """Validate internal API key for worker access"""
    if not x_internal_key:
        raise HTTPException(
            status_code=401,
            detail="Internal API key required",
        )
    
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid internal API key",
        )
    
    return x_internal_key
