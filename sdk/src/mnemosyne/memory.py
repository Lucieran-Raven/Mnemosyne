"""
Memory models and types for Mnemosyne SDK
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memory entities"""
    PREFERENCE = "preference"
    FACT = "fact"
    ENTITY = "entity"
    INTENT = "intent"
    EXPERIENCE = "experience"
    RELATIONSHIP = "relationship"


class Memory(BaseModel):
    """Represents a stored memory"""
    
    id: UUID
    content: str
    memory_type: MemoryType
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime
    recency_score: float = Field(ge=0.0, le=1.0, default=1.0)
    extracted_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class MemorySearchResult(BaseModel):
    """Result from a memory search query"""
    
    query: str
    memories: list[Memory]
    total_found: int
    search_time_ms: int


class StoreRequest(BaseModel):
    """Request to store a memory"""
    
    content: str = Field(..., min_length=1, max_length=10000)
    memory_type: Optional[MemoryType] = MemoryType.FACT
    metadata: Optional[Dict[str, Any]] = None
    async_processing: bool = True


class StoreResponse(BaseModel):
    """Response from store operation"""
    
    status: str
    message: str
    job_id: Optional[UUID] = None
    memory_ids: Optional[list[UUID]] = None
    processed: bool = False


class JobStatus(BaseModel):
    """Status of an async distillation job"""
    
    job_id: UUID
    status: str  # pending, processing, completed, failed
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_memory_ids: Optional[list[UUID]] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
