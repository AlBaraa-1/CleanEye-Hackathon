"""
File Converter Tool - Convert between different file formats
"""
import logging
from typing import Dict, Any
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


def convert_file(input_path: str, output_format: str, output_path: str = None) -> Dict[str, Any]:
    """
    Convert a file from one format to another.
    
    Supported conversions:
    - PDF to TXT
    - TXT to CSV (assumes structured text)
    - CSV to TXT
    - Any text-based format conversions
    
    Args:
        input_path: Path to input file
        output_format: Desired output format ('txt', 'csv', 'pdf')
        output_path: Optional output path; auto-generated if not provided
        
    Returns:
        Dictionary with conversion results
    """
    try:
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Determine input format
        input_format = input_file.suffix.lower().replace('.', '')
        
        # Generate output path if not provided
        if output_path is None:
            output_path = str(input_file.parent / f"{input_file.stem}.{output_format}")
        
        output_file = Path(output_path)
        
        # Perform conversion based on formats
        if input_format == 'pdf' and output_format == 'txt':
            success, message = _pdf_to_txt(input_path, output_path)
            
        elif input_format == 'txt' and output_format == 'csv':
            success, message = _txt_to_csv(input_path, output_path)
            
        elif input_format == 'csv' and output_format == 'txt':
            success, message = _csv_to_txt(input_path, output_path)
            
        elif input_format in ['txt', 'md', 'log'] and output_format in ['txt', 'md', 'log']:
            success, message = _text_to_text(input_path, output_path)
            
        else:
            raise ValueError(f"Conversion from {input_format} to {output_format} not supported")
        
        return {
            "output_path": str(output_file),
            "success": success,
            "message": message,
            "input_format": input_format,
            "output_format": output_format,
            "file_size_bytes": output_file.stat().st_size if output_file.exists() else 0
        }
        
    except Exception as e:
        logger.error(f"Error converting file: {e}")
        raise


def _pdf_to_txt(input_path: str, output_path: str) -> tuple:
    """Convert PDF to TXT"""
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(input_path)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        full_text = "\n\n".join(text_parts)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        return True, f"Successfully converted PDF to TXT ({len(reader.pages)} pages)"
        
    except Exception as e:
        logger.error(f"PDF to TXT conversion error: {e}")
        return False, str(e)


def _txt_to_csv(input_path: str, output_path: str) -> tuple:
    """Convert TXT to CSV (assumes tab or comma separated values)"""
    try:
        import pandas as pd
        
        # Try to read as CSV with different delimiters
        try:
            df = pd.read_csv(input_path, sep='\t')
        except:
            try:
                df = pd.read_csv(input_path, sep=',')
            except:
                # If not structured, create simple CSV with one column
                with open(input_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                df = pd.DataFrame({'text': [line.strip() for line in lines if line.strip()]})
        
        df.to_csv(output_path, index=False)
        
        return True, f"Successfully converted TXT to CSV ({len(df)} rows)"
        
    except Exception as e:
        logger.error(f"TXT to CSV conversion error: {e}")
        return False, str(e)


def _csv_to_txt(input_path: str, output_path: str) -> tuple:
    """Convert CSV to TXT"""
    try:
        import pandas as pd
        
        df = pd.read_csv(input_path)
        
        # Convert to formatted text
        text = df.to_string(index=False)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return True, f"Successfully converted CSV to TXT ({len(df)} rows)"
        
    except Exception as e:
        logger.error(f"CSV to TXT conversion error: {e}")
        return False, str(e)


def _text_to_text(input_path: str, output_path: str) -> tuple:
    """Convert between text-based formats"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "Successfully converted text file"
        
    except Exception as e:
        logger.error(f"Text to text conversion error: {e}")
        return False, str(e)


def batch_convert(input_files: list, output_format: str) -> Dict[str, Any]:
    """
    Convert multiple files to the same output format.
    
    Args:
        input_files: List of input file paths
        output_format: Desired output format for all files
        
    Returns:
        Dictionary with batch conversion results
    """
    results = []
    
    for input_file in input_files:
        try:
            result = convert_file(input_file, output_format)
            result["input_file"] = input_file
            results.append(result)
        except Exception as e:
            logger.error(f"Error converting {input_file}: {e}")
            results.append({
                "input_file": input_file,
                "success": False,
                "message": str(e)
            })
    
    successful = sum(1 for r in results if r.get("success", False))
    
    return {
        "total_files": len(input_files),
        "successful": successful,
        "failed": len(input_files) - successful,
        "results": results
    }
