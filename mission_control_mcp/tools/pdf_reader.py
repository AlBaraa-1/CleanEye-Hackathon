"""
PDF Reader Tool - Extract text and metadata from PDF files
"""
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def read_pdf(file_path: str) -> Dict[str, Any]:
    """
    Read and extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing extracted text, page count, and metadata
    """
    try:
        from PyPDF2 import PdfReader
        
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Read PDF
        reader = PdfReader(file_path)
        
        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {page_num} ---\n{text}")
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {e}")
                text_parts.append(f"--- Page {page_num} ---\n[Extraction failed]")
        
        full_text = "\n\n".join(text_parts)
        
        # Extract metadata
        metadata = {}
        if reader.metadata:
            metadata = {
                "author": reader.metadata.get("/Author", "Unknown"),
                "creator": reader.metadata.get("/Creator", "Unknown"),
                "producer": reader.metadata.get("/Producer", "Unknown"),
                "subject": reader.metadata.get("/Subject", "Unknown"),
                "title": reader.metadata.get("/Title", "Unknown"),
                "creation_date": str(reader.metadata.get("/CreationDate", "Unknown"))
            }
        
        return {
            "text": full_text,
            "pages": len(reader.pages),
            "metadata": metadata
        }
        
    except ImportError:
        logger.error("PyPDF2 not installed. Install with: pip install pypdf2")
        raise
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        raise


def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic information about a PDF without extracting all text.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with PDF information
    """
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(file_path)
        
        return {
            "page_count": len(reader.pages),
            "is_encrypted": reader.is_encrypted,
            "file_size_bytes": Path(file_path).stat().st_size,
            "file_name": Path(file_path).name
        }
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        raise
