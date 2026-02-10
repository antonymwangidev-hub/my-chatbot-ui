"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ===========================
# Enums
# ===========================

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ===========================
# Chat Models
# ===========================

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime


# ===========================
# Document Models
# ===========================

class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    size: int


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    status: DocumentStatus
    chunk_count: Optional[int] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


# ===========================
# RAG Models
# ===========================

class RetrievalResult(BaseModel):
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str


class RAGContext(BaseModel):
    query: str
    retrieved_chunks: List[RetrievalResult]
    total_chunks: int


# ===========================
# Admin Models
# ===========================

class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_conversations: int
    active_sessions: int
    avg_response_time: float
    uptime: str


class DocumentList(BaseModel):
    documents: List[DocumentMetadata]
    total: int
    page: int
    page_size: int


# ===========================
# Database Models (SQLAlchemy)
# ===========================

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class DBConversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)


class DBMessage(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)
    role = Column(String(50))
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, nullable=True)


class DBDocument(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), unique=True, index=True)
    filename = Column(String(500))
    content_type = Column(String(100))
    size = Column(Integer)
    status = Column(String(50))
    chunk_count = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)


class DBAnalytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    query = Column(Text)
    response_time = Column(Float)
    chunks_retrieved = Column(Integer)
    user_rating = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, nullable=True)
