"""
Text Extractor Tool - Clean, summarize, and process text
"""
import logging
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import clean_text, chunk_text, summarize_text, extract_keywords

logger = logging.getLogger(__name__)


def extract_text(text: str, operation: str = "clean", max_length: int = 500) -> Dict[str, Any]:
    """
    Process text based on the specified operation.
    
    Args:
        text: Raw text to process
        operation: Operation to perform - 'clean', 'summarize', 'chunk', or 'keywords'
        max_length: Maximum length for summary operations
        
    Returns:
        Dictionary containing processed text and metadata
    """
    try:
        if not text or not text.strip():
            raise ValueError("Input text is empty")
        
        result = ""
        metadata = {}
        
        if operation == "clean":
            result = clean_text(text)
            metadata = {
                "operation": "clean",
                "original_length": len(text),
                "cleaned_length": len(result)
            }
            
        elif operation == "summarize":
            result = summarize_text(text, max_length)
            metadata = {
                "operation": "summarize",
                "original_length": len(text),
                "summary_length": len(result),
                "compression_ratio": round(len(result) / len(text), 2) if len(text) > 0 else 0
            }
            
        elif operation == "chunk":
            chunks = chunk_text(text, chunk_size=max_length, overlap=50)
            result = "\n\n---CHUNK---\n\n".join(chunks)
            metadata = {
                "operation": "chunk",
                "total_chunks": len(chunks),
                "chunk_size": max_length
            }
            
        elif operation == "keywords":
            keywords = extract_keywords(text, top_n=10)
            result = ", ".join(keywords)
            metadata = {
                "operation": "keywords",
                "keyword_count": len(keywords),
                "keywords": keywords
            }
            
        else:
            raise ValueError(f"Unknown operation: {operation}. Use 'clean', 'summarize', 'chunk', or 'keywords'")
        
        # Calculate word count
        word_count = len(result.split())
        
        return {
            "result": result,
            "word_count": word_count,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        raise


def process_multiple_texts(texts: list, operation: str = "clean") -> list:
    """
    Process multiple texts with the same operation.
    
    Args:
        texts: List of text strings to process
        operation: Operation to apply to all texts
        
    Returns:
        List of results for each text
    """
    results = []
    for idx, text in enumerate(texts):
        try:
            result = extract_text(text, operation)
            result["index"] = idx
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing text at index {idx}: {e}")
            results.append({
                "index": idx,
                "error": str(e),
                "result": "",
                "word_count": 0
            })
    
    return results
