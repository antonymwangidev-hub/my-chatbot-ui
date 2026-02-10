"""
Pydantic and SQLAlchemy models for the AI Business Chatbot
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Pydantic Imports
from pydantic import BaseModel, Field

# SQLAlchemy Imports
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# ===========================
# 1. ENUMS (Must be first)
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
# 2. PYDANTIC MODELS (Schemas)
# ===========================

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    extra_info: Optional[Dict[str, Any]] = Field(None, alias="metadata")

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
    extra_info: Optional[Dict[str, Any]] = Field(None, alias="metadata")

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

class DocumentList(BaseModel):
    documents: List[DocumentMetadata]
    total: int
    page: int
    page_size: int

class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_conversations: int
    active_sessions: int
    avg_response_time: float
    uptime: str

# ===========================
# 3. DATABASE MODELS (SQLAlchemy)
# ===========================

Base = declarative_base()

class DBConversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    # Renamed to avoid SQLAlchemy conflict
    context_data = Column(JSON, nullable=True)

class DBMessage(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)
    role = Column(String(50))
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # Renamed to avoid SQLAlchemy conflict
    msg_metadata = Column(JSON, nullable=True)

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
    # Renamed to avoid SQLAlchemy conflict
    doc_metadata = Column(JSON, nullable=True)
