"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import get_db
from app.services.redis_cache import RedisCache
from app.services.pinecone_client import PineconeClient

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Basic health check endpoint"""
    try:
        # Check database
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with all services"""
    checks = {
        "database": "unknown",
        "redis": "unknown",
        "pinecone": "unknown",
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis = RedisCache()
        await redis.connect()
        await redis.ping()
        checks["redis"] = "healthy"
        await redis.disconnect()
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    # Check Pinecone
    try:
        pinecone = PineconeClient()
        await pinecone.connect()
        stats = await pinecone.get_stats()
        checks["pinecone"] = f"healthy ({stats.get('total_vector_count', 0)} vectors)"
    except Exception as e:
        checks["pinecone"] = f"unhealthy: {str(e)}"
    
    all_healthy = all(status == "healthy" or status.startswith("healthy") 
                      for status in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes-style readiness probe"""
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}


@router.get("/live")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"alive": True}
