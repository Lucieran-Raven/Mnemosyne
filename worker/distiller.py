"""
Mnemosyne Async Distillation Worker

Background worker service that processes memory distillation jobs asynchronously.
Uses Gemini 2.5 Flash for fast, cost-effective extraction.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
import httpx
import google.generativeai as genai
from pydantic import BaseModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemoryType:
    PREFERENCE = "preference"
    FACT = "fact"
    ENTITY = "entity"
    INTENT = "intent"
    EXPERIENCE = "experience"
    RELATIONSHIP = "relationship"


class DistilledMemory(BaseModel):
    """A memory extracted by the distillation process"""
    id: str
    content: str
    memory_type: str
    confidence: float
    extracted_data: Dict[str, Any]
    source_content: str
    created_at: datetime


@dataclass
class DistillationJob:
    """A job to distill memories from content"""
    job_id: UUID
    user_id: str
    content: str
    memory_type: Optional[str]
    metadata: Dict[str, Any]
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_memory_ids: List[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.result_memory_ids is None:
            self.result_memory_ids = []


class GeminiDistiller:
    """Uses Gemini 2.5 Flash for fast, cheap distillation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        
        # Distillation prompt
        self.distillation_prompt = """You are an expert at extracting structured memories from conversations.

Given a conversation or text, extract meaningful memories that would help an AI assistant better serve the user.

Extract memories of these types:
- PREFERENCE: User likes/dislikes, choices, opinions
- FACT: Important facts about the user, their life, work
- ENTITY: People, places, organizations mentioned
- INTENT: Goals, plans, things user wants to do
- EXPERIENCE: Past experiences, stories shared
- RELATIONSHIP: Connections between entities

For each memory extracted, provide:
1. content: A clear, concise statement of the memory
2. memory_type: One of the types above
3. confidence: 0.0-1.0 score of how certain this extraction is
4. extracted_data: Structured key-value pairs (e.g., {"dietary_restriction": "gluten-free"})

Content to analyze:
{content}

Respond in this exact JSON format:
{
  "memories": [
    {
      "content": "string",
      "memory_type": "PREFERENCE|FACT|ENTITY|INTENT|EXPERIENCE|RELATIONSHIP",
      "confidence": 0.95,
      "extracted_data": {"key": "value"}
    }
  ]
}

Only extract high-quality, useful memories. If nothing meaningful can be extracted, return empty memories array."""

    async def distill(self, content: str) -> List[DistilledMemory]:
        """Distill memories from content using Gemini"""
        try:
            prompt = self.distillation_prompt.format(content=content)
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                )
            )
            
            # Parse JSON response
            text = response.text
            # Extract JSON from potential markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            memories = []
            
            for mem_data in data.get("memories", []):
                memory = DistilledMemory(
                    id=str(uuid4()),
                    content=mem_data["content"],
                    memory_type=mem_data["memory_type"],
                    confidence=mem_data["confidence"],
                    extracted_data=mem_data.get("extracted_data", {}),
                    source_content=content,
                    created_at=datetime.utcnow()
                )
                memories.append(memory)
            
            logger.info(f"Distilled {len(memories)} memories from content")
            return memories
            
        except Exception as e:
            logger.error(f"Distillation failed: {e}")
            return []


class WorkerService:
    """Background worker that processes distillation jobs"""
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        api_base_url: str = "http://localhost:8000",
        poll_interval: float = 1.0,
        max_concurrent: int = 5
    ):
        self.distiller = GeminiDistiller(gemini_api_key)
        self.api_base_url = api_base_url
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self.running = False
        self.jobs: Dict[UUID, DistillationJob] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
    async def fetch_pending_jobs(self) -> List[DistillationJob]:
        """Fetch pending jobs from API queue"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/internal/jobs/pending",
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    jobs = []
                    for job_data in data.get("jobs", []):
                        job = DistillationJob(
                            job_id=UUID(job_data["job_id"]),
                            user_id=job_data["user_id"],
                            content=job_data["content"],
                            memory_type=job_data.get("memory_type"),
                            metadata=job_data.get("metadata", {}),
                            status="pending"
                        )
                        jobs.append(job)
                    return jobs
                else:
                    logger.warning(f"Failed to fetch jobs: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            return []
    
    async def update_job_status(
        self,
        job_id: UUID,
        status: str,
        memory_ids: Optional[List[str]] = None,
        error: Optional[str] = None
    ):
        """Update job status in API"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "status": status,
                    "memory_ids": memory_ids or [],
                    "error": error
                }
                response = await client.post(
                    f"{self.api_base_url}/internal/jobs/{job_id}/status",
                    json=payload,
                    timeout=10.0
                )
                if response.status_code != 200:
                    logger.warning(f"Failed to update job {job_id}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
    
    async def store_memory(
        self,
        user_id: str,
        memory: DistilledMemory,
        job_metadata: Dict[str, Any]
    ) -> Optional[str]:
        """Store a distilled memory in the API"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "user_id": user_id,
                    "content": memory.content,
                    "memory_type": memory.memory_type,
                    "confidence": memory.confidence,
                    "extracted_data": memory.extracted_data,
                    "source_job_id": str(job_metadata.get("job_id", "")),
                }
                response = await client.post(
                    f"{self.api_base_url}/v1/memories/store",
                    json=payload,
                    timeout=10.0
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    return data.get("memory_id")
                else:
                    logger.warning(f"Failed to store memory: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return None
    
    async def process_job(self, job: DistillationJob):
        """Process a single distillation job"""
        async with self._semaphore:
            logger.info(f"Processing job {job.job_id}")
            job.status = "processing"
            job.started_at = datetime.utcnow()
            
            try:
                # Distill memories
                memories = await self.distiller.distill(job.content)
                
                if not memories:
                    logger.info(f"No memories extracted for job {job.job_id}")
                    job.status = "completed"
                    job.completed_at = datetime.utcnow()
                    await self.update_job_status(job.job_id, "completed", [])
                    return
                
                # Store each memory
                memory_ids = []
                for memory in memories:
                    memory_id = await self.store_memory(
                        job.user_id,
                        memory,
                        {"job_id": job.job_id}
                    )
                    if memory_id:
                        memory_ids.append(memory_id)
                        job.result_memory_ids.append(memory_id)
                
                job.status = "completed"
                job.completed_at = datetime.utcnow()
                await self.update_job_status(job.job_id, "completed", memory_ids)
                
                logger.info(f"Job {job.job_id} completed with {len(memory_ids)} memories")
                
            except Exception as e:
                logger.error(f"Job {job.job_id} failed: {e}")
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                await self.update_job_status(job.job_id, "failed", error=str(e))
    
    async def run(self):
        """Main worker loop"""
        logger.info("Worker service starting...")
        self.running = True
        
        while self.running:
            try:
                # Fetch pending jobs
                jobs = await self.fetch_pending_jobs()
                
                if jobs:
                    logger.info(f"Fetched {len(jobs)} pending jobs")
                    
                    # Process all jobs concurrently (up to max_concurrent)
                    tasks = [self.process_job(job) for job in jobs]
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait before next poll
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(self.poll_interval)
        
        logger.info("Worker service stopped")
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        logger.info("Worker stop requested")


async def main():
    """Run the worker service"""
    # Get API key from environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    api_url = os.getenv("MNEMOSYNE_API_URL", "http://localhost:8000")
    
    if not gemini_key:
        logger.error("GEMINI_API_KEY environment variable required")
        return
    
    # Create and run worker
    worker = WorkerService(
        gemini_api_key=gemini_key,
        api_base_url=api_url,
        poll_interval=1.0,
        max_concurrent=5
    )
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
