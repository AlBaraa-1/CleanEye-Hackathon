"""
RAG Search Tool - Semantic search using vector embeddings
"""
import logging
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rag_utils import semantic_search, create_rag_store

logger = logging.getLogger(__name__)


def search_documents(query: str, documents: List[str], top_k: int = 3) -> Dict[str, Any]:
    """
    Perform semantic search on a collection of documents.
    
    Args:
        query: Search query string
        documents: List of document strings to search
        top_k: Number of top results to return
        
    Returns:
        Dictionary containing search results with scores
    """
    try:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not documents or len(documents) == 0:
            raise ValueError("Documents list cannot be empty")
        
        # Perform semantic search
        results = semantic_search(query, documents, top_k)
        
        return {
            "query": query,
            "total_documents": len(documents),
            "returned_results": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error performing RAG search: {e}")
        raise


def build_knowledge_base(documents: List[str]) -> Dict[str, Any]:
    """
    Build a knowledge base from documents for later querying.
    
    Args:
        documents: List of documents to index
        
    Returns:
        Dictionary with knowledge base info
    """
    try:
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        # Create RAG store
        store = create_rag_store(documents)
        
        return {
            "success": True,
            "document_count": len(documents),
            "message": "Knowledge base built successfully",
            "store": store  # In a real scenario, this would be persisted
        }
        
    except Exception as e:
        logger.error(f"Error building knowledge base: {e}")
        raise


def multi_query_search(queries: List[str], documents: List[str], top_k: int = 3) -> Dict[str, Any]:
    """
    Perform multiple searches with different queries on the same document set.
    
    Args:
        queries: List of query strings
        documents: List of documents to search
        top_k: Number of results per query
        
    Returns:
        Dictionary with results for each query
    """
    try:
        if not queries or not documents:
            raise ValueError("Both queries and documents must be provided")
        
        # Build store once for efficiency
        store = create_rag_store(documents)
        
        all_results = {}
        for idx, query in enumerate(queries):
            try:
                results = store.search(query, top_k)
                all_results[f"query_{idx+1}"] = {
                    "query": query,
                    "results": results
                }
            except Exception as e:
                logger.error(f"Error searching query {idx+1}: {e}")
                all_results[f"query_{idx+1}"] = {
                    "query": query,
                    "error": str(e),
                    "results": []
                }
        
        return {
            "total_queries": len(queries),
            "total_documents": len(documents),
            "results": all_results
        }
        
    except Exception as e:
        logger.error(f"Error in multi-query search: {e}")
        raise


def find_similar_documents(target_doc: str, documents: List[str], top_k: int = 5) -> Dict[str, Any]:
    """
    Find documents similar to a target document.
    
    Args:
        target_doc: The document to find similar ones for
        documents: Corpus of documents to search
        top_k: Number of similar documents to return
        
    Returns:
        Dictionary with similar documents
    """
    try:
        if not target_doc or not documents:
            raise ValueError("Target document and documents list must be provided")
        
        # Use target doc as query
        results = semantic_search(target_doc, documents, top_k)
        
        return {
            "target_document": target_doc[:200] + "..." if len(target_doc) > 200 else target_doc,
            "corpus_size": len(documents),
            "similar_documents": results
        }
        
    except Exception as e:
        logger.error(f"Error finding similar documents: {e}")
        raise
