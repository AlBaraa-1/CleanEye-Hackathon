"""
Web Fetcher Tool - Fetch and extract content from web pages
"""
import logging
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import validate_url, clean_text, format_timestamp

logger = logging.getLogger(__name__)


def fetch_web_content(url: str, extract_text_only: bool = True, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch content from a web URL.
    
    Args:
        url: URL to fetch
        extract_text_only: If True, extract only text content; if False, return HTML
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing fetched content, status code, and metadata
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Validate URL
        if not validate_url(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch content
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        content = ""
        content_type = response.headers.get('Content-Type', '')
        
        if extract_text_only and 'text/html' in content_type:
            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Further clean
            content = clean_text(content)
            
        else:
            # Return raw content
            content = response.text
        
        # Build metadata
        metadata = {
            "url": url,
            "status_code": response.status_code,
            "content_type": content_type,
            "content_length": len(content),
            "encoding": response.encoding,
            "timestamp": format_timestamp(),
            "headers": dict(response.headers)
        }
        
        return {
            "content": content,
            "status_code": response.status_code,
            "metadata": metadata
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching web content: {e}")
        raise


def fetch_multiple_urls(urls: list, extract_text_only: bool = True) -> list:
    """
    Fetch content from multiple URLs.
    
    Args:
        urls: List of URLs to fetch
        extract_text_only: Whether to extract text only
        
    Returns:
        List of results for each URL
    """
    results = []
    for idx, url in enumerate(urls):
        try:
            result = fetch_web_content(url, extract_text_only)
            result["index"] = idx
            result["success"] = True
            results.append(result)
        except Exception as e:
            logger.error(f"Error fetching URL at index {idx} ({url}): {e}")
            results.append({
                "index": idx,
                "url": url,
                "success": False,
                "error": str(e),
                "content": "",
                "status_code": 0
            })
    
    return results


def extract_links(url: str) -> Dict[str, Any]:
    """
    Extract all links from a web page.
    
    Args:
        url: URL to extract links from
        
    Returns:
        Dictionary with extracted links
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            links.append({
                "text": link.get_text(strip=True),
                "href": absolute_url
            })
        
        return {
            "url": url,
            "total_links": len(links),
            "links": links
        }
        
    except Exception as e:
        logger.error(f"Error extracting links: {e}")
        raise
