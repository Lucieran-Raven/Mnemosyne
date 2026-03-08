"""
Internal Job Queue Router

Endpoints for background worker to fetch and update distillation jobs.
These are internal endpoints not exposed to public API.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import structlog

from app.services.memory_service import MemoryService
from app.services.auth import get_internal_api_key

logger = structlog.get_logger()
router = APIRouter(prefix="/internal", tags=["Internal"])

# In-memory job queue (replace with Redis/PostgreSQL in production)
_job_queue: dict = {}
_pending_jobs: List[UUID] = []
_processing_jobs: dict = {}
_completed_jobs: dict = {}


class CreateJobRequest(BaseModel):
    user_id: str
    content: str
    memory_type: Optional[str] = None
    metadata: dict = {}


class JobResponse(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime
    message: str


class JobStatusUpdate(BaseModel):
    status: str  # processing, completed, failed
    memory_ids: List[str] = []
    error: Optional[str] = None


class PendingJobsResponse(BaseModel):
    jobs: List[dict]


def create_job(user_id: str, content: str, memory_type: Optional[str], metadata: dict) -> UUID:
    """Create a new distillation job"""
    job_id = UUID(int=datetime.utcnow().timestamp())
    
    job_data = {
        "job_id": str(job_id),
        "user_id": user_id,
        "content": content,
        "memory_type": memory_type,
        "metadata": metadata,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "result_memory_ids": [],
        "error_message": None,
    }
    
    _job_queue[job_id] = job_data
    _pending_jobs.append(job_id)
    
    logger.info("Job created", job_id=str(job_id), user_id=user_id)
    return job_id


@router.get("/jobs/pending", response_model=PendingJobsResponse)
async def get_pending_jobs(
    api_key: str = Depends(get_internal_api_key)
) -> PendingJobsResponse:
    """Fetch pending jobs for worker processing"""
    jobs = []
    
    # Get up to 10 pending jobs
    for job_id in _pending_jobs[:10]:
        if job_id in _job_queue:
            job_data = _job_queue[job_id]
            jobs.append({
                "job_id": job_data["job_id"],
                "user_id": job_data["user_id"],
                "content": job_data["content"],
                "memory_type": job_data["memory_type"],
                "metadata": job_data["metadata"],
            })
            
            # Mark as processing
            job_data["status"] = "processing"
            job_data["started_at"] = datetime.utcnow().isoformat()
            _processing_jobs[job_id] = job_data
    
    # Clear fetched jobs from pending
    _pending_jobs[:] = _pending_jobs[10:]
    
    logger.info(f"Fetched {len(jobs)} pending jobs")
    return PendingJobsResponse(jobs=jobs)


@router.post("/jobs/{job_id}/status")
async def update_job_status(
    job_id: UUID,
    update: JobStatusUpdate,
    api_key: str = Depends(get_internal_api_key)
):
    """Update job status from worker"""
    if job_id not in _job_queue and job_id not in _processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get job data
    job_data = _job_queue.get(job_id) or _processing_jobs.get(job_id)
    
    # Update status
    job_data["status"] = update.status
    job_data["result_memory_ids"] = update.memory_ids
    
    if update.error:
        job_data["error_message"] = update.error
    
    if update.status in ("completed", "failed"):
        job_data["completed_at"] = datetime.utcnow().isoformat()
        
        # Move to completed
        if job_id in _processing_jobs:
            _completed_jobs[job_id] = job_data
            del _processing_jobs[job_id]
        
        logger.info(
            f"Job {update.status}",
            job_id=str(job_id),
            memory_count=len(update.memory_ids)
        )
    
    return {"status": "updated"}


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: UUID,
    api_key: str = Depends(get_internal_api_key)
):
    """Get job details"""
    job_data = (
        _job_queue.get(job_id) or 
        _processing_jobs.get(job_id) or 
        _completed_jobs.get(job_id)
    )
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_data


# Cleanup function for old jobs
def cleanup_old_jobs(max_age_hours: int = 24):
    """Remove old completed jobs from memory"""
    cutoff = datetime.utcnow() - __import__('datetime').timedelta(hours=max_age_hours)
    
    to_remove = []
    for job_id, job_data in _completed_jobs.items():
        completed_at = job_data.get("completed_at")
        if completed_at:
            completed_time = datetime.fromisoformat(completed_at)
            if completed_time < cutoff:
                to_remove.append(job_id)
    
    for job_id in to_remove:
        del _completed_jobs[job_id]
        if job_id in _job_queue:
            del _job_queue[job_id]
    
    logger.info(f"Cleaned up {len(to_remove)} old jobs")
