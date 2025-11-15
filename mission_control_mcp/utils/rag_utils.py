"""
RAG (Retrieval Augmented Generation) utilities using FAISS and embeddings
"""
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SimpleRAGStore:
    """
    Simple RAG implementation using FAISS for vector similarity search
    """
    
    def __init__(self):
        """Initialize the RAG store"""
        self.documents: List[str] = []
        self.embeddings: List[np.ndarray] = []
        self.index = None
        self._model = None
        
    def _get_model(self):
        """Lazy load the sentence transformer model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.error(f"Failed to load sentence transformer: {e}")
                raise
        return self._model
    
    def add_documents(self, documents: List[str]) -> None:
        """
        Add documents to the RAG store and build FAISS index.
        
        Args:
            documents: List of document strings to add
        """
        import faiss
        
        if not documents:
            logger.warning("No documents provided to add")
            return
            
        self.documents.extend(documents)
        
        # Generate embeddings
        model = self._get_model()
        new_embeddings = model.encode(documents, show_progress_bar=False)
        self.embeddings.extend(new_embeddings)
        
        # Build or update FAISS index
        embeddings_array = np.array(self.embeddings).astype('float32')
        dimension = embeddings_array.shape[1]
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings_array)
        logger.info(f"Added {len(documents)} documents to RAG store")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar documents using the query.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of search results with scores
        """
        if self.index is None or len(self.documents) == 0:
            logger.warning("No documents in RAG store")
            return []
        
        # Encode query
        model = self._get_model()
        query_embedding = model.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search FAISS index
        top_k = min(top_k, len(self.documents))
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score (inverse relationship)
                similarity_score = 1.0 / (1.0 + float(distance))
                results.append({
                    "rank": i + 1,
                    "document": self.documents[idx],
                    "score": round(similarity_score, 4),
                    "distance": float(distance)
                })
        
        return results
    
    def clear(self) -> None:
        """Clear all documents and reset the index"""
        self.documents = []
        self.embeddings = []
        self.index = None
        logger.info("Cleared RAG store")


def create_rag_store(documents: List[str]) -> SimpleRAGStore:
    """
    Factory function to create and populate a RAG store.
    
    Args:
        documents: List of documents to add to store
        
    Returns:
        Initialized SimpleRAGStore instance
    """
    store = SimpleRAGStore()
    if documents:
        store.add_documents(documents)
    return store


def semantic_search(query: str, documents: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Perform semantic search on a list of documents.
    
    Args:
        query: Search query
        documents: List of documents to search
        top_k: Number of results to return
        
    Returns:
        List of search results
    """
    store = create_rag_store(documents)
    return store.search(query, top_k)
