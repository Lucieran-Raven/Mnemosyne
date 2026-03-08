"""
Mnemosyne API - Main FastAPI Application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import get_settings
from app.db.database import init_db, close_db
from app.api.routes import memories, health, internal
from app.services.redis_cache import RedisCache
from app.services.pinecone_client import PineconeClient

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Mnemosyne API", version=settings.APP_VERSION)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize external services
    app.state.redis = RedisCache()
    app.state.pinecone = PineconeClient()
    
    await app.state.redis.connect()
    logger.info("Redis cache connected")
    
    await app.state.pinecone.connect()
    logger.info("Pinecone vector store connected")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mnemosyne API")
    await close_db()
    await app.state.redis.disconnect()
    logger.info("Connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Memory Layer for Agents - Store, retrieve, and manage persistent agent memories",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        },
    )


# Include routers
app.include_router(internal.router, prefix="/internal")
app.include_router(health.router, tags=["Health"])
app.include_router(memories.router, prefix="/v1/memories", tags=["Memories"])


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
