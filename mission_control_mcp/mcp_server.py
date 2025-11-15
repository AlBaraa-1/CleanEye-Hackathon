"""
MissionControlMCP - Enterprise Automation MCP Server
Main server implementation using MCP SDK
"""
import logging
from typing import Any
import sys
import os

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import MCP SDK
from mcp.server import Server
from mcp.types import Tool, TextContent

# Import tool functions
from tools.pdf_reader import read_pdf
from tools.text_extractor import extract_text
from tools.web_fetcher import fetch_web_content
from tools.rag_search import search_documents
from tools.data_visualizer import visualize_data
from tools.file_converter import convert_file
from tools.email_intent_classifier import classify_email_intent
from tools.kpi_generator import generate_kpis

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("mission-control-mcp")


# Tool definitions
TOOLS = [
    Tool(
        name="pdf_reader",
        description="Extract text and metadata from PDF files. Reads all pages and extracts document information.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the PDF file to read"
                }
            },
            "required": ["file_path"]
        }
    ),
    Tool(
        name="text_extractor",
        description="Process and extract information from text. Supports cleaning, summarization, chunking, and keyword extraction.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Raw text to process"
                },
                "operation": {
                    "type": "string",
                    "description": "Operation: 'clean', 'summarize', 'chunk', or 'keywords'",
                    "enum": ["clean", "summarize", "chunk", "keywords"],
                    "default": "clean"
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length for summary or chunk size",
                    "default": 500
                }
            },
            "required": ["text"]
        }
    ),
    Tool(
        name="web_fetcher",
        description="Fetch and extract content from web URLs. Returns clean text or HTML content with metadata.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch content from"
                },
                "extract_text_only": {
                    "type": "boolean",
                    "description": "Extract only text content (removes HTML)",
                    "default": True
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="rag_search",
        description="Semantic search using RAG (Retrieval Augmented Generation). Finds relevant documents using vector embeddings.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of documents to search in"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results to return",
                    "default": 3
                }
            },
            "required": ["query", "documents"]
        }
    ),
    Tool(
        name="data_visualizer",
        description="Create data visualizations and charts. Supports bar, line, pie, and scatter charts from JSON or CSV data.",
        inputSchema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "JSON or CSV string data"
                },
                "chart_type": {
                    "type": "string",
                    "description": "Chart type",
                    "enum": ["bar", "line", "pie", "scatter"],
                    "default": "bar"
                },
                "x_column": {
                    "type": "string",
                    "description": "X-axis column name"
                },
                "y_column": {
                    "type": "string",
                    "description": "Y-axis column name"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title",
                    "default": "Data Visualization"
                }
            },
            "required": ["data"]
        }
    ),
    Tool(
        name="file_converter",
        description="Convert files between formats. Supports PDF↔TXT, TXT↔CSV conversions.",
        inputSchema={
            "type": "object",
            "properties": {
                "input_path": {
                    "type": "string",
                    "description": "Path to input file"
                },
                "output_format": {
                    "type": "string",
                    "description": "Desired output format",
                    "enum": ["txt", "csv", "pdf"]
                },
                "output_path": {
                    "type": "string",
                    "description": "Optional output file path"
                }
            },
            "required": ["input_path", "output_format"]
        }
    ),
    Tool(
        name="email_intent_classifier",
        description="Classify email intent using NLP. Identifies inquiry, complaint, request, feedback, meeting, order, urgent, follow-up, thank you, and application intents.",
        inputSchema={
            "type": "object",
            "properties": {
                "email_text": {
                    "type": "string",
                    "description": "Email text to classify"
                }
            },
            "required": ["email_text"]
        }
    ),
    Tool(
        name="kpi_generator",
        description="Generate business KPIs and insights from data. Calculates revenue, growth, efficiency, customer, and operational metrics.",
        inputSchema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "JSON string with business data"
                },
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["revenue", "growth", "efficiency", "customer", "operational"]
                    },
                    "description": "List of metrics to calculate",
                    "default": ["revenue", "growth", "efficiency"]
                }
            },
            "required": ["data"]
        }
    )
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool execution requests
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        List of TextContent responses
    """
    try:
        logger.info(f"Executing tool: {name}")
        
        result = None
        
        if name == "pdf_reader":
            result = read_pdf(arguments["file_path"])
            
        elif name == "text_extractor":
            result = extract_text(
                text=arguments["text"],
                operation=arguments.get("operation", "clean"),
                max_length=arguments.get("max_length", 500)
            )
            
        elif name == "web_fetcher":
            result = fetch_web_content(
                url=arguments["url"],
                extract_text_only=arguments.get("extract_text_only", True)
            )
            
        elif name == "rag_search":
            result = search_documents(
                query=arguments["query"],
                documents=arguments["documents"],
                top_k=arguments.get("top_k", 3)
            )
            
        elif name == "data_visualizer":
            result = visualize_data(
                data=arguments["data"],
                chart_type=arguments.get("chart_type", "bar"),
                x_column=arguments.get("x_column"),
                y_column=arguments.get("y_column"),
                title=arguments.get("title", "Data Visualization")
            )
            
        elif name == "file_converter":
            result = convert_file(
                input_path=arguments["input_path"],
                output_format=arguments["output_format"],
                output_path=arguments.get("output_path")
            )
            
        elif name == "email_intent_classifier":
            result = classify_email_intent(arguments["email_text"])
            
        elif name == "kpi_generator":
            result = generate_kpis(
                data=arguments["data"],
                metrics=arguments.get("metrics", ["revenue", "growth", "efficiency"])
            )
            
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Format result as JSON string
        import json
        result_text = json.dumps(result, indent=2, default=str)
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point for the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MissionControlMCP server starting...")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
