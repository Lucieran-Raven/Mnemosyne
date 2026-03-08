"""
Database models for Mnemosyne API
"""

import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy import (
    String, Text, Float, DateTime, ForeignKey, 
    Index, JSON, Enum as SQLEnum, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class MemoryType(str, Enum):
    """Types of memory entities"""
    PREFERENCE = "preference"
    FACT = "fact"
    ENTITY = "entity"
    INTENT = "intent"
    EXPERIENCE = "experience"
    RELATIONSHIP = "relationship"


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    external_id: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True,
        comment="Clerk user ID or external auth provider ID"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), 
        unique=True, 
        index=True,
        nullable=True
    )
    api_key: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True,
        default=lambda: str(uuid.uuid4()).replace("-", "")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    memories: Mapped[List["Memory"]] = relationship(
        "Memory", 
        back_populates="user",
        lazy="selectin"
    )
    access_logs: Mapped[List["AccessLog"]] = relationship(
        "AccessLog",
        back_populates="user",
        lazy="selectin"
    )
    
    # Subscription info
    tier: Mapped[str] = mapped_column(String(50), default="free")
    monthly_operations: Mapped[int] = mapped_column(Integer, default=0)
    operation_limit: Mapped[int] = mapped_column(Integer, default=100000)


class Memory(Base):
    """Core memory entity - metadata stored in PostgreSQL"""
    __tablename__ = "memories"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Memory content (for backup/reference)
    content: Mapped[str] = mapped_column(Text)
    memory_type: Mapped[MemoryType] = mapped_column(SQLEnum(MemoryType))
    
    # Structured data extracted during distillation
    extracted_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment="Structured facts extracted from raw content"
    )
    
    # Vector reference (actual vector stored in Pinecone)
    vector_id: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True
    )
    
    # Metadata for filtering and ranking
    confidence: Mapped[float] = mapped_column(
        Float, 
        default=0.9,
        comment="Confidence score from distillation"
    )
    recency_score: Mapped[float] = mapped_column(
        Float, 
        default=1.0,
        comment="Temporal weighting factor"
    )
    access_count: Mapped[int] = mapped_column(
        Integer, 
        default=0,
        comment="Number of times this memory was retrieved"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Optional expiration for transient memories"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memories")
    conflicts: Mapped[List["MemoryConflict"]] = relationship(
        "MemoryConflict",
        foreign_keys="MemoryConflict.memory_id",
        back_populates="memory",
        lazy="selectin"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_memories_user_created", "user_id", "created_at"),
        Index("ix_memories_user_type", "user_id", "memory_type"),
        Index("ix_memories_vector_lookup", "user_id", "vector_id"),
    )


class MemoryConflict(Base):
    """Track conflicting memories for resolution"""
    __tablename__ = "memory_conflicts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("memories.id", ondelete="CASCADE"),
        index=True
    )
    conflicting_memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("memories.id", ondelete="CASCADE"),
        index=True
    )
    
    # Conflict metadata
    similarity_score: Mapped[float] = mapped_column(
        Float,
        comment="Cosine similarity between conflicting memories"
    )
    resolution_strategy: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="How conflict was resolved: keep_both, replace, merge"
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    
    # Relationships
    memory: Mapped["Memory"] = relationship(
        "Memory",
        foreign_keys=[memory_id],
        back_populates="conflicts"
    )


class DistillationJob(Base):
    """Track async distillation jobs"""
    __tablename__ = "distillation_jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Job status
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        comment="pending, processing, completed, failed"
    )
    
    # Input data
    raw_content: Mapped[str] = mapped_column(Text)
    conversation_context: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment="Full conversation context if available"
    )
    
    # Output data
    result_memory_ids: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        comment="List of created memory IDs"
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Cloud Tasks reference
    cloud_task_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Performance metrics
    processing_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Time taken to process in milliseconds"
    )
    tokens_used: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="LLM tokens consumed"
    )


class AccessLog(Base):
    """Audit log for API access"""
    __tablename__ = "access_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Request details
    endpoint: Mapped[str] = mapped_column(String(255), index=True)
    method: Mapped[str] = mapped_column(String(10))
    status_code: Mapped[int] = mapped_column(Integer)
    
    # Request metadata
    request_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int] = mapped_column(Integer)
    
    # Client info
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Operation type for billing
    operation_type: Mapped[str] = mapped_column(
        String(50),
        comment="store, retrieve, delete, etc."
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        index=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="access_logs")
    
    __table_args__ = (
        Index("ix_access_logs_user_time", "user_id", "created_at"),
        Index("ix_access_logs_endpoint_time", "endpoint", "created_at"),
    )


class MemoryDecayLog(Base):
    """Log of memory decay operations for analytics"""
    __tablename__ = "memory_decay_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("memories.id", ondelete="CASCADE"),
        index=True
    )
    
    old_recency_score: Mapped[float] = mapped_column(Float)
    new_recency_score: Mapped[float] = mapped_column(Float)
    decay_reason: Mapped[str] = mapped_column(
        String(50),
        comment="time_decay, access_boost, conflict_resolution"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
