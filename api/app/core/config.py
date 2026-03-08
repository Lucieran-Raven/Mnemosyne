"""
Mnemosyne API Configuration
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Mnemosyne API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    API_KEY_HEADER: str = "X-API-Key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mnemosyne"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # Vector Database (Pinecone)
    PINECONE_API_KEY: str = ""
    PINECONE_HOST: str = ""
    PINECONE_INDEX_NAME: str = "mnemosyne-memories"
    VECTOR_DIMENSION: int = 768
    
    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-exp"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    GEMINI_MAX_TOKENS: int = 1000
    GEMINI_TEMPERATURE: float = 0.1
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_REGION: str = "us-central1"
    CLOUD_TASKS_QUEUE: str = "mnemosyne-distillation"
    
    # Clerk Auth
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    
    # Internal Worker Auth
    INTERNAL_API_KEY: str = "dev-internal-key-change-in-production"
    
    # Memory Processing
    MAX_MEMORY_SIZE: int = 10000  # characters
    DEFAULT_TOP_K: int = 5
    TEMPORAL_DECAY_HOURS: float = 168.0  # 7 days
    CONFLICT_THRESHOLD: float = 0.85  # cosine similarity
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Multi-tenancy
    TENANT_ISOLATION_MODE: str = "shared_schema"  # shared_schema, schema_per_user, db_per_user
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"
    
    @property
    def cors_origins(self) -> List[str]:
        if self.is_production:
            return [
                "https://mnemosyne.dev",
                "https://dashboard.mnemosyne.dev",
                "https://api.mnemosyne.dev",
            ]
        return ["*"]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
