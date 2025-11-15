"""
Pydantic schemas for tool inputs and outputs
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PdfReaderInput(BaseModel):
    """Input schema for PDF reader tool"""
    file_path: str = Field(description="Path to the PDF file to read")


class PdfReaderOutput(BaseModel):
    """Output schema for PDF reader tool"""
    text: str = Field(description="Extracted text from PDF")
    pages: int = Field(description="Number of pages in PDF")
    metadata: Dict[str, Any] = Field(description="PDF metadata")


class TextExtractorInput(BaseModel):
    """Input schema for text extractor tool"""
    text: str = Field(description="Raw text to process")
    operation: str = Field(description="Operation: 'clean', 'summarize', or 'chunk'", default="clean")
    max_length: Optional[int] = Field(description="Max length for summary", default=500)


class TextExtractorOutput(BaseModel):
    """Output schema for text extractor tool"""
    result: str = Field(description="Processed text")
    word_count: int = Field(description="Word count of result")


class WebFetcherInput(BaseModel):
    """Input schema for web fetcher tool"""
    url: str = Field(description="URL to fetch")
    extract_text_only: bool = Field(description="Extract only text content", default=True)


class WebFetcherOutput(BaseModel):
    """Output schema for web fetcher tool"""
    content: str = Field(description="Fetched content")
    status_code: int = Field(description="HTTP status code")
    metadata: Dict[str, Any] = Field(description="Response metadata")


class RagSearchInput(BaseModel):
    """Input schema for RAG search tool"""
    query: str = Field(description="Search query")
    documents: List[str] = Field(description="List of documents to search in")
    top_k: int = Field(description="Number of top results to return", default=3)


class RagSearchOutput(BaseModel):
    """Output schema for RAG search tool"""
    results: List[Dict[str, Any]] = Field(description="Search results with scores")


class DataVisualizerInput(BaseModel):
    """Input schema for data visualizer tool"""
    data: str = Field(description="JSON or CSV string data")
    chart_type: str = Field(description="Chart type: 'bar', 'line', 'pie', 'scatter'", default="bar")
    x_column: Optional[str] = Field(description="X-axis column name", default=None)
    y_column: Optional[str] = Field(description="Y-axis column name", default=None)
    title: Optional[str] = Field(description="Chart title", default="Data Visualization")


class DataVisualizerOutput(BaseModel):
    """Output schema for data visualizer tool"""
    image_base64: str = Field(description="Base64 encoded chart image")
    dimensions: Dict[str, int] = Field(description="Image dimensions")


class FileConverterInput(BaseModel):
    """Input schema for file converter tool"""
    input_path: str = Field(description="Path to input file")
    output_format: str = Field(description="Output format: 'txt', 'csv', 'pdf'")
    output_path: Optional[str] = Field(description="Path for output file", default=None)


class FileConverterOutput(BaseModel):
    """Output schema for file converter tool"""
    output_path: str = Field(description="Path to converted file")
    success: bool = Field(description="Conversion success status")
    message: str = Field(description="Status message")


class EmailIntentInput(BaseModel):
    """Input schema for email intent classifier tool"""
    email_text: str = Field(description="Email text to classify")


class EmailIntentOutput(BaseModel):
    """Output schema for email intent classifier tool"""
    intent: str = Field(description="Classified intent category")
    confidence: float = Field(description="Confidence score (0-1)")
    secondary_intents: List[Dict[str, float]] = Field(description="Other possible intents")


class KpiGeneratorInput(BaseModel):
    """Input schema for KPI generator tool"""
    data: str = Field(description="JSON string with business data")
    metrics: List[str] = Field(description="List of metrics to calculate", default=["revenue", "growth", "efficiency"])


class KpiGeneratorOutput(BaseModel):
    """Output schema for KPI generator tool"""
    kpis: Dict[str, Any] = Field(description="Calculated KPIs")
    summary: str = Field(description="Executive summary")
    trends: List[str] = Field(description="Key trends identified")
