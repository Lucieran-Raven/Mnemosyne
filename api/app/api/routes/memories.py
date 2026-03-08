"""
Memory API routes - Core store/retrieve endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.db.database import get_db
from app.models.models import Memory, User, DistillationJob, MemoryType, AccessLog
from app.services.auth import get_current_user
from app.services.memory_service import MemoryService
from app.services.distillation_service import DistillationService
from app.core.config import get_settings
from pydantic import BaseModel, Field

settings = get_settings()
router = APIRouter()


# Pydantic models for API
class StoreMemoryRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=settings.MAX_MEMORY_SIZE)
    memory_type: Optional[MemoryType] = MemoryType.FACT
    metadata: Optional[dict] = Field(default=None, description="Optional metadata")
    async_processing: bool = Field(default=True, description="Process asynchronously via queue")


class StoreMemoryResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[UUID] = None
    memory_ids: Optional[List[UUID]] = None
    processed: bool = False


class RetrieveMemoryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    memory_type: Optional[MemoryType] = None
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryResponse(BaseModel):
    id: UUID
    content: str
    memory_type: MemoryType
    confidence: float
    created_at: str
    recency_score: float
    extracted_data: Optional[dict] = None


class RetrieveMemoryResponse(BaseModel):
    query: str
    results: List[MemoryResponse]
    total_found: int
    search_time_ms: int


class DeleteMemoryResponse(BaseModel):
    deleted: bool
    message: str


@router.post("/store", response_model=StoreMemoryResponse)
async def store_memory(
    request: StoreMemoryRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Store a new memory for the user.
    
    By default, memories are processed asynchronously for distillation.
    Set async_processing=false for synchronous processing.
    """
    # Check rate limits
    if current_user.monthly_operations >= current_user.operation_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly operation limit reached ({current_user.operation_limit})"
        )
    
    memory_service = MemoryService(db)
    
    if request.async_processing:
        # Queue for async processing
        job = await memory_service.queue_distillation(
            user_id=current_user.id,
            content=request.content,
            memory_type=request.memory_type,
            metadata=request.metadata,
        )
        
        # Increment operation count
        current_user.monthly_operations += 1
        await db.commit()
        
        return StoreMemoryResponse(
            status="accepted",
            message="Memory queued for processing",
            job_id=job.id,
            processed=False,
        )
    else:
        # Synchronous processing
        memories = await memory_service.store_memory_sync(
            user_id=current_user.id,
            content=request.content,
            memory_type=request.memory_type,
            metadata=request.metadata,
        )
        
        current_user.monthly_operations += 1
        await db.commit()
        
        return StoreMemoryResponse(
            status="completed",
            message=f"Stored {len(memories)} memories",
            memory_ids=[m.id for m in memories],
            processed=True,
        )


@router.post("/retrieve", response_model=RetrieveMemoryResponse)
async def retrieve_memories(
    request: RetrieveMemoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve relevant memories based on natural language query.
    
    Uses semantic search with temporal weighting to return most relevant,
    recent memories first.
    """
    import time
    start_time = time.time()
    
    memory_service = MemoryService(db)
    
    # Perform hybrid search
    memories = await memory_service.retrieve_memories(
        user_id=current_user.id,
        query=request.query,
        top_k=request.top_k,
        memory_type=request.memory_type,
        min_confidence=request.min_confidence,
    )
    
    search_time = int((time.time() - start_time) * 1000)
    
    # Update access count for retrieved memories
    for memory in memories:
        memory.access_count += 1
    await db.commit()
    
    # Log access
    current_user.monthly_operations += 1
    await db.commit()
    
    return RetrieveMemoryResponse(
        query=request.query,
        results=[
            MemoryResponse(
                id=m.id,
                content=m.content,
                memory_type=m.memory_type,
                confidence=m.confidence,
                created_at=m.created_at.isoformat(),
                recency_score=m.recency_score,
                extracted_data=m.extracted_data,
            )
            for m in memories
        ],
        total_found=len(memories),
        search_time_ms=search_time,
    )


@router.get("/list", response_model=List[MemoryResponse])
async def list_memories(
    memory_type: Optional[MemoryType] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's memories with optional filtering"""
    
    query = select(Memory).where(Memory.user_id == current_user.id)
    
    if memory_type:
        query = query.where(Memory.memory_type == memory_type)
    
    query = query.order_by(desc(Memory.created_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    memories = result.scalars().all()
    
    return [
        MemoryResponse(
            id=m.id,
            content=m.content,
            memory_type=m.memory_type,
            confidence=m.confidence,
            created_at=m.created_at.isoformat(),
            recency_score=m.recency_score,
            extracted_data=m.extracted_data,
        )
        for m in memories
    ]


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific memory by ID"""
    
    query = select(Memory).where(
        and_(Memory.id == memory_id, Memory.user_id == current_user.id)
    )
    result = await db.execute(query)
    memory = result.scalar_one_or_none()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return MemoryResponse(
        id=memory.id,
        content=memory.content,
        memory_type=memory.memory_type,
        confidence=memory.confidence,
        created_at=memory.created_at.isoformat(),
        recency_score=memory.recency_score,
        extracted_data=memory.extracted_data,
    )


@router.delete("/{memory_id}", response_model=DeleteMemoryResponse)
async def delete_memory(
    memory_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a specific memory"""
    
    memory_service = MemoryService(db)
    deleted = await memory_service.delete_memory(
        user_id=current_user.id,
        memory_id=memory_id,
    )
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    current_user.monthly_operations += 1
    await db.commit()
    
    return DeleteMemoryResponse(
        deleted=True,
        message="Memory deleted successfully",
    )


@router.get("/job/{job_id}/status")
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check status of async distillation job"""
    
    query = select(DistillationJob).where(
        and_(DistillationJob.id == job_id, DistillationJob.user_id == current_user.id)
    )
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "result_memory_ids": job.result_memory_ids,
        "error_message": job.error_message,
        "processing_time_ms": job.processing_time_ms,
    }
