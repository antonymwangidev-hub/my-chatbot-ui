"""
Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from pathlib import Path
from loguru import logger
import sys

from config import settings
from models import (
    ChatRequest, ChatResponse, DocumentMetadata,
    SystemStats, DocumentList, DocumentStatus
)
from rag_engine import rag_engine
from vector_store import vector_store
from memory import conversation_memory
from document_loader import document_loader

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL
)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Intelligent AI Chatbot with RAG for Business Support"
)

# ===========================
# UPDATED CORS SETTINGS
# ===========================
# This allows your GitHub Pages site to communicate with this Render backend.
origins = [
    "http://localhost:3000",
    "https://antonymwangidev-hub.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
os.makedirs("logs", exist_ok=True)


# ===========================
# CHAT ENDPOINTS
# ===========================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user queries with RAG
    """
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id or not conversation_memory.get_session(session_id):
            session_id = conversation_memory.create_session(request.user_id)
        
        # Get conversation history
        history = conversation_memory.get_formatted_history(session_id, limit=10)
        
        # Add user message to history
        conversation_memory.add_message(
            session_id=session_id,
            role="user",
            content=request.message
        )
        
        # Process with RAG
        result = rag_engine.query(
            user_query=request.message,
            conversation_history=history
        )
        
        # Add assistant response to history
        conversation_memory.add_message(
            session_id=session_id,
            role="assistant",
            content=result["answer"],
            metadata={
                "sources": result["sources"],
                "tokens_used": result["tokens_used"]
            }
        )
        
        return ChatResponse(
            message=result["answer"],
            session_id=session_id,
            sources=result["sources"],
            confidence=result["confidence"],
            metadata={
                "response_time": result["response_time"],
                "chunks_retrieved": result["retrieved_chunks"],
                "model": result["model_used"]
            }
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ... [The rest of the endpoints from main.py remain the same] ...
# Make sure to include all other endpoints (get_chat_history, upload_document, etc.) from your original file.
