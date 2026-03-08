"""
Core memory service - Business logic for store/retrieve operations
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload

from app.models.models import Memory, User, DistillationJob, MemoryType, MemoryConflict
from app.services.pinecone_client import PineconeClient
from app.services.redis_cache import RedisCache
from app.services.embedding_service import EmbeddingService
from app.core.config import get_settings

settings = get_settings()


class MemoryService:
    """Core memory operations service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
    
    async def queue_distillation(
        self,
        user_id: UUID,
        content: str,
        memory_type: MemoryType,
        metadata: Optional[dict] = None,
    ) -> DistillationJob:
        """Queue memory for async distillation processing via job queue"""
        
        # Create job record in database
        job = DistillationJob(
            user_id=user_id,
            raw_content=content,
            status="pending",
            conversation_context=metadata,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        # Add to in-memory job queue for worker to pick up
        try:
            from app.api.routes.internal import create_job
            create_job(
                user_id=str(user_id),
                content=content,
                memory_type=memory_type.value if memory_type else None,
                metadata=metadata or {},
            )
        except Exception as e:
            # If queue fails, job stays in DB for worker polling
            import logging
            logging.getLogger(__name__).warning(f"Could not add to job queue: {e}")
        
        return job
    
    async def store_memory_sync(
        self,
        user_id: UUID,
        content: str,
        memory_type: MemoryType,
        metadata: Optional[dict] = None,
    ) -> List[Memory]:
        """Synchronous memory storage with immediate distillation"""
        
        from app.services.distillation_service import DistillationService
        
        distillation = DistillationService(self.db)
        
        # Run distillation immediately
        extracted_memories = await distillation.distill_memory(
            content=content,
            context=metadata,
        )
        
        # Store each extracted memory
        stored_memories = []
        for extracted in extracted_memories:
            memory = await self._create_memory(
                user_id=user_id,
                content=extracted.get("text", content),
                memory_type=MemoryType(extracted.get("type", memory_type.value)),
                extracted_data=extracted,
                confidence=extracted.get("confidence", 0.9),
            )
            stored_memories.append(memory)
        
        return stored_memories
    
    async def _create_memory(
        self,
        user_id: UUID,
        content: str,
        memory_type: MemoryType,
        extracted_data: Optional[dict] = None,
        confidence: float = 0.9,
    ) -> Memory:
        """Create and store a single memory with vector embedding"""
        
        # Generate embedding
        embedding = await self.embedding_service.embed_text(content)
        
        # Create memory record
        vector_id = str(uuid4())
        memory = Memory(
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            extracted_data=extracted_data,
            vector_id=vector_id,
            confidence=confidence,
            recency_score=1.0,  # Fresh memory
        )
        
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        
        # Store vector in Pinecone
        pinecone = PineconeClient()
        await pinecone.connect()
        
        await pinecone.upsert_vectors(
            vectors=[{
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "user_id": str(user_id),
                    "memory_id": str(memory.id),
                    "memory_type": memory_type.value,
                    "confidence": confidence,
                    "created_at": datetime.utcnow().isoformat(),
                },
            }],
            namespace=str(user_id),  # Namespace per user for isolation
        )
        
        # Check for conflicts
        await self._check_conflicts(user_id, memory, embedding)
        
        return memory
    
    async def _check_conflicts(
        self,
        user_id: UUID,
        new_memory: Memory,
        new_embedding: List[float],
    ):
        """Check for conflicting memories and record them"""
        
        # Query similar memories
        pinecone = PineconeClient()
        await pinecone.connect()
        
        similar = await pinecone.query_vectors(
            vector=new_embedding,
            top_k=5,
            namespace=str(user_id),
            filter={"memory_id": {"$ne": str(new_memory.id)}},  # Exclude self
        )
        
        # Record conflicts for high similarity
        for match in similar:
            if match["score"] > settings.CONFLICT_THRESHOLD:
                conflict = MemoryConflict(
                    memory_id=new_memory.id,
                    conflicting_memory_id=UUID(match["metadata"]["memory_id"]),
                    similarity_score=match["score"],
                )
                self.db.add(conflict)
        
        await self.db.commit()
    
    async def retrieve_memories(
        self,
        user_id: UUID,
        query: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_confidence: float = 0.5,
    ) -> List[Memory]:
        """
        Retrieve memories using semantic search with temporal weighting.
        """
        
        # Check cache first
        import hashlib
        query_hash = hashlib.md5(f"{user_id}:{query}:{top_k}:{memory_type}".encode()).hexdigest()
        
        redis = RedisCache()
        await redis.connect()
        
        cached = await redis.get_search_cache(str(user_id), query_hash)
        if cached:
            # Fetch full memories from cache
            memory_ids = [UUID(m["id"]) for m in cached]
            query = select(Memory).where(Memory.id.in_(memory_ids))
            result = await self.db.execute(query)
            memories = result.scalars().all()
            return sorted(memories, key=lambda m: memory_ids.index(m.id))
        
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Search Pinecone
        pinecone = PineconeClient()
        await pinecone.connect()
        
        filter_dict = {"confidence": {"$gte": min_confidence}}
        if memory_type:
            filter_dict["memory_type"] = memory_type.value
        
        vector_results = await pinecone.query_vectors(
            vector=query_embedding,
            top_k=top_k * 2,  # Get more to apply temporal weighting
            namespace=str(user_id),
            filter=filter_dict,
        )
        
        if not vector_results:
            return []
        
        # Fetch full memory records
        memory_ids = [UUID(r["metadata"]["memory_id"]) for r in vector_results]
        
        query = select(Memory).where(
            and_(
                Memory.id.in_(memory_ids),
                Memory.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        memories = {m.id: m for m in result.scalars().all()}
        
        # Apply temporal weighting and re-rank
        scored_memories = []
        for vr in vector_results:
            memory_id = UUID(vr["metadata"]["memory_id"])
            if memory_id in memories:
                memory = memories[memory_id]
                # Combined score: semantic similarity * recency * access boost
                final_score = (
                    vr["score"] * 
                    memory.recency_score * 
                    (1 + 0.1 * min(memory.access_count, 10))  # Access boost
                )
                scored_memories.append((final_score, memory))
        
        # Sort by score and take top_k
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = [m for _, m in scored_memories[:top_k]]
        
        # Cache results
        cache_data = [
            {"id": str(m.id), "score": s}
            for s, m in scored_memories[:top_k]
        ]
        await redis.set_search_cache(str(user_id), query_hash, cache_data)
        
        return results
    
    async def delete_memory(
        self,
        user_id: UUID,
        memory_id: UUID,
    ) -> bool:
        """Delete a memory and its vector"""
        
        # Get memory
        query = select(Memory).where(
            and_(Memory.id == memory_id, Memory.user_id == user_id)
        )
        result = await self.db.execute(query)
        memory = result.scalar_one_or_none()
        
        if not memory:
            return False
        
        # Delete from Pinecone
        pinecone = PineconeClient()
        await pinecone.connect()
        await pinecone.delete_vectors([memory.vector_id], namespace=str(user_id))
        
        # Delete from PostgreSQL
        await self.db.delete(memory)
        await self.db.commit()
        
        # Invalidate cache
        redis = RedisCache()
        await redis.connect()
        await redis.invalidate_memory_cache(str(user_id), str(memory_id))
        
        return True
    
    async def update_recency_scores(self, user_id: UUID):
        """
        Update recency scores based on time decay.
        Called periodically by background job.
        """
        from sqlalchemy import func
        
        # Get all user memories
        query = select(Memory).where(Memory.user_id == user_id)
        result = await self.db.execute(query)
        memories = result.scalars().all()
        
        now = datetime.utcnow()
        
        for memory in memories:
            age_hours = (now - memory.created_at).total_seconds() / 3600
            
            # Exponential decay: score = exp(-age / decay_constant)
            import math
            decay_constant = settings.TEMPORAL_DECAY_HOURS
            new_score = math.exp(-age_hours / decay_constant)
            
            # Boost for frequently accessed memories
            access_boost = min(memory.access_count * 0.05, 0.3)
            new_score = min(new_score + access_boost, 1.0)
            
            memory.recency_score = new_score
        
        await self.db.commit()
