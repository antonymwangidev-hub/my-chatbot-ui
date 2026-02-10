"""
Anthropic Claude API Client
"""
from anthropic import Anthropic
from typing import List, Dict, Any, Optional
from loguru import logger

from config import settings


class ClaudeClient:
    """Client for interacting with Anthropic's Claude API"""
    
    def __init__(self):
        """Initialize Claude client"""
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    def generate_response(
        self,
        user_message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Claude
        
        Args:
            user_message: The user's message/query
            context: RAG context (retrieved documents)
            conversation_history: Previous messages in the conversation
            system_prompt: Custom system prompt
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Build system prompt
            if system_prompt is None:
                system_prompt = self._build_system_prompt(context)
            
            # Build messages
            messages = []
            
            # Add conversation history if exists
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )
            
            # Extract response text
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text
            
            logger.info(f"Generated response (tokens: {response.usage.output_tokens})")
            
            return {
                "response": response_text,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "stop_reason": response.stop_reason
            }
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            raise
    
    def _build_system_prompt(self, context: Optional[str] = None) -> str:
        """Build the system prompt with RAG context"""
        base_prompt = """You are an AI assistant for a business, helping customers with their questions and concerns.

Your responsibilities:
- Provide accurate, helpful answers based on the company's knowledge base
- Be professional, friendly, and concise
- If you don't know something, admit it and suggest contacting human support
- Always prioritize customer satisfaction

Guidelines:
- Use the provided context to answer questions accurately
- Don't make up information not in the context
- Be conversational but professional
- Keep responses focused and relevant
"""
        
        if context:
            context_prompt = f"""
RELEVANT INFORMATION FROM KNOWLEDGE BASE:
{context}

Use the above information to answer the customer's question. If the information doesn't fully answer their question, let them know what you can help with based on available information.
"""
            return base_prompt + context_prompt
        
        return base_prompt
    
    def generate_embedding_query(self, text: str) -> str:
        """
        Optimize a user query for better retrieval
        (This is a simple version - can be enhanced)
        """
        # Could use Claude to rephrase/expand the query for better retrieval
        return text


# Singleton instance
claude_client = ClaudeClient()
