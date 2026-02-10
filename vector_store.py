"""
Vector Store Service using ChromaDB for semantic search
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from loguru import logger
import uuid

from config import settings


class VectorStore:
    """Handles vector database operations with ChromaDB"""
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model"""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Load embedding model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=settings.COLLECTION_NAME
            )
            logger.info(f"Loaded existing collection: {settings.COLLECTION_NAME}")
        except:
            self.collection = self.client.create_collection(
                name=settings.COLLECTION_NAME,
                metadata={"description": "Business documents for RAG"}
            )
            logger.info(f"Created new collection: {settings.COLLECTION_NAME}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dicts
            ids: Optional list of IDs (auto-generated if not provided)
        
        Returns:
            List of document IDs
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = [self.generate_embedding(doc) for doc in documents]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
        return ids
    
    def search(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
        
        Returns:
            Dictionary with results
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })
        
        logger.info(f"Found {len(formatted_results)} results for query")
        return {
            'results': formatted_results,
            'query': query,
            'total': len(formatted_results)
        }
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Deleted document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def delete_by_source(self, source_filename: str) -> int:
        """Delete all chunks from a specific source file"""
        try:
            # Get all documents with this source
            results = self.collection.get(
                where={"source": source_filename}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                count = len(results['ids'])
                logger.info(f"Deleted {count} chunks from {source_filename}")
                return count
            return 0
        except Exception as e:
            logger.error(f"Error deleting source {source_filename}: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': settings.COLLECTION_NAME,
            'embedding_model': settings.EMBEDDING_MODEL
        }
    
    def reset_collection(self):
        """Delete all documents (use with caution!)"""
        self.client.delete_collection(name=settings.COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=settings.COLLECTION_NAME
        )
        logger.warning("Collection reset - all documents deleted!")


# Singleton instance
vector_store = VectorStore()
