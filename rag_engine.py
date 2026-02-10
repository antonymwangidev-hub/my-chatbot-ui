"""
RAG (Retrieval-Augmented Generation) Engine
Combines vector search with Claude for intelligent responses
"""
from typing import List, Dict, Any, Optional
from loguru import logger
import time

from vector_store import vector_store
from claude_client import claude_client
from config import settings


class RAGEngine:
    """Main RAG processing engine"""
    
    def __init__(self):
        self.vector_store = vector_store
        self.claude_client = claude_client
    
    def query(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Process a user query using RAG
        
        Args:
            user_query: User's question
            conversation_history: Previous conversation messages
            filter_metadata: Filters for document retrieval
            top_k: Number of documents to retrieve
        
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Retrieving documents for query: {user_query[:100]}")
            retrieval_results = self.vector_store.search(
                query=user_query,
                top_k=top_k or settings.TOP_K_RESULTS,
                filter_metadata=filter_metadata
            )
            
            retrieved_docs = retrieval_results['results']
            
            # Step 2: Build context from retrieved documents
            context = self._build_context(retrieved_docs)
            
            # Step 3: Generate response with Claude
            logger.info("Generating response with Claude")
            claude_response = self.claude_client.generate_response(
                user_message=user_query,
                context=context,
                conversation_history=conversation_history
            )
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Step 4: Prepare sources information
            sources = self._format_sources(retrieved_docs)
            
            return {
                "answer": claude_response["response"],
                "sources": sources,
                "retrieved_chunks": len(retrieved_docs),
                "response_time": round(total_time, 2),
                "model_used": claude_response["model"],
                "tokens_used": claude_response["usage"],
                "confidence": self._calculate_confidence(retrieved_docs)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            raise
    
    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents"""
        if not retrieved_docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            # Filter by similarity threshold
            if doc['distance'] < (1 - settings.SIMILARITY_THRESHOLD):
                source = doc['metadata'].get('source', 'Unknown')
                chunk_text = doc['content']
                context_parts.append(
                    f"[Source {i}: {source}]\n{chunk_text}\n"
                )
        
        context = "\n---\n".join(context_parts)
        return context
    
    def _format_sources(self, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information for the response"""
        sources = []
        seen_sources = set()
        
        for doc in retrieved_docs:
            source_name = doc['metadata'].get('source', 'Unknown')
            if source_name not in seen_sources:
                sources.append({
                    'source': source_name,
                    'relevance': round(1 - doc['distance'], 2),
                    'page': doc['metadata'].get('page', None),
                    'section': doc['metadata'].get('section', None)
                })
                seen_sources.add(source_name)
        
        return sources
    
    def _calculate_confidence(self, retrieved_docs: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieval quality"""
        if not retrieved_docs:
            return 0.0
        
        # Use average similarity of top 3 results
        top_results = retrieved_docs[:3]
        avg_similarity = sum(1 - doc['distance'] for doc in top_results) / len(top_results)
        
        return round(avg_similarity, 2)
    
    def add_feedback(
        self,
        query: str,
        response: str,
        rating: int,
        feedback_text: Optional[str] = None
    ):
        """
        Store user feedback for improving the system
        (Can be extended to fine-tune retrieval or prompts)
        """
        logger.info(f"Received feedback - Rating: {rating}/5")
        # TODO: Store in database for analytics


# Singleton instance
rag_engine = RAGEngine()
