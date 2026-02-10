"""
Conversation Memory Manager
Handles session management and conversation history
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from collections import defaultdict
from loguru import logger

from config import settings


class ConversationMemory:
    """Manages conversation sessions and history"""
    
    def __init__(self):
        # In-memory storage (use Redis for production)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.message_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new conversation session
        
        Args:
            user_id: Optional user identifier
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'is_active': True,
            'metadata': {}
        }
        
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self.sessions.get(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a message to conversation history
        
        Args:
            session_id: Session identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Additional metadata
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found, creating new session")
            self.sessions[session_id] = {
                'session_id': session_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'is_active': True
            }
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        self.message_history[session_id].append(message)
        
        # Update last activity
        self.sessions[session_id]['last_activity'] = datetime.now()
        
        # Trim history if too long
        max_history = settings.MAX_CONVERSATION_HISTORY
        if len(self.message_history[session_id]) > max_history * 2:  # *2 for user+assistant pairs
            self.message_history[session_id] = self.message_history[session_id][-max_history * 2:]
    
    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return
        
        Returns:
            List of messages
        """
        history = self.message_history.get(session_id, [])
        
        if limit:
            return history[-limit:]
        
        return history
    
    def get_formatted_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for Claude API
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages
        
        Returns:
            List of messages in Claude format
        """
        history = self.get_history(session_id, limit)
        
        formatted = []
        for msg in history:
            formatted.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        return formatted
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.message_history:
            self.message_history[session_id] = []
            logger.info(f"Cleared history for session: {session_id}")
    
    def end_session(self, session_id: str):
        """End a conversation session"""
        if session_id in self.sessions:
            self.sessions[session_id]['is_active'] = False
            logger.info(f"Ended session: {session_id}")
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions (run periodically)"""
        timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        now = datetime.now()
        
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if now - session['last_activity'] > timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            if session_id in self.message_history:
                del self.message_history[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return {}
        
        history = self.message_history.get(session_id, [])
        user_messages = [m for m in history if m['role'] == 'user']
        assistant_messages = [m for m in history if m['role'] == 'assistant']
        
        return {
            'session_id': session_id,
            'total_messages': len(history),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'created_at': session['created_at'],
            'last_activity': session['last_activity'],
            'duration_minutes': (session['last_activity'] - session['created_at']).total_seconds() / 60,
            'is_active': session['is_active']
        }
    
    def get_all_active_sessions(self) -> List[str]:
        """Get list of all active session IDs"""
        return [
            sid for sid, session in self.sessions.items()
            if session.get('is_active', True)
        ]


# Singleton instance
conversation_memory = ConversationMemory()
