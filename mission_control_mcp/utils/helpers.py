"""
Helper utility functions
"""
import re
import logging
from typing import List, Dict, Any
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace, special characters, etc.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text string
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', '', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for processing.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        
    return chunks


def summarize_text(text: str, max_length: int = 500) -> str:
    """
    Create a simple extractive summary by taking the first sentences.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        
    Returns:
        Summarized text
    """
    sentences = re.split(r'[.!?]+', text)
    summary = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
            
    return summary.strip()


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract top keywords from text using simple frequency analysis.
    
    Args:
        text: Text to analyze
        top_n: Number of top keywords to return
        
    Returns:
        List of keywords
    """
    # Simple word frequency approach
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    
    # Remove common stop words
    stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 
                  'will', 'would', 'could', 'should', 'about', 'their', 'there'}
    words = [w for w in words if w not in stop_words]
    
    # Count frequency
    word_freq: Dict[str, int] = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:top_n]]


def validate_url(url: str) -> bool:
    """
    Validate if a string is a proper URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def format_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


def parse_json_safe(json_str: str) -> Dict[str, Any]:
    """
    Safely parse JSON string with error handling.
    
    Args:
        json_str: JSON string to parse
        
    Returns:
        Parsed dictionary or empty dict on error
    """
    import json
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {}
