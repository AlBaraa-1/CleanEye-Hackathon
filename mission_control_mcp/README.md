# 🚀 MissionControlMCP

**Enterprise Automation MCP Server for Document Analysis, Data Processing & Business Intelligence**

A fully functional Model Context Protocol (MCP) server providing 8 powerful enterprise automation tools for document processing, web scraping, semantic search, data visualization, and business analytics.

Built for the **MCP 1st Birthday Hackathon – Winter 2025** (Track 1).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tools](#tools)
- [Installation](#installation)
- [Usage](#usage)
- [Tool Examples](#tool-examples)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Development](#development)
- [Testing](#testing)
- [Architecture](#architecture)
- [Hackathon Submission](#hackathon-submission)

---

## 🎯 Overview

**MissionControlMCP** is an enterprise-grade MCP server that provides intelligent automation capabilities through 8 specialized tools. It enables AI assistants like Claude to perform complex document processing, data analysis, web research, and business intelligence tasks.

### Key Capabilities

- **📄 Document Processing**: Extract text from PDFs, process and summarize content
- **🌐 Web Intelligence**: Fetch and parse web content with clean text extraction
- **🔍 Semantic Search**: RAG-based vector search using FAISS and sentence transformers
- **📊 Data Visualization**: Generate charts from CSV/JSON data
- **🔄 File Conversion**: Convert between PDF, TXT, and CSV formats
- **📧 Email Classification**: Classify email intents using NLP
- **📈 KPI Generation**: Calculate business metrics and generate insights

---

## ✨ Features

- ✅ **8 Production-Ready Tools** for enterprise automation
- ✅ **MCP Compliant** - Works with Claude Desktop and any MCP client
- ✅ **Type-Safe** - Built with Python 3.11+ and type hints
- ✅ **Modular Architecture** - Clean separation of concerns
- ✅ **Comprehensive Testing** - Test suite included
- ✅ **Well Documented** - Clear schemas and examples
- ✅ **Vector Search** - RAG implementation with FAISS
- ✅ **Data Visualization** - Base64 encoded chart generation
- ✅ **NLP Classification** - Rule-based intent detection

---

## 🛠️ Tools

### 1. **pdf_reader**
Extract text and metadata from PDF files.

**Input:**
- `file_path`: Path to PDF file

**Output:**
- Extracted text from all pages
- Page count
- Document metadata (author, title, dates)

---

### 2. **text_extractor**
Process and extract information from text.

**Input:**
- `text`: Raw text to process
- `operation`: 'clean', 'summarize', 'chunk', or 'keywords'
- `max_length`: Max length for summaries (default: 500)

**Output:**
- Processed text
- Word count
- Operation metadata

---

### 3. **web_fetcher**
Fetch and extract content from web URLs.

**Input:**
- `url`: URL to fetch
- `extract_text_only`: Extract text only (default: true)

**Output:**
- Clean text content or HTML
- HTTP status code
- Response metadata

---

### 4. **rag_search**
Semantic search using RAG (Retrieval Augmented Generation).

**Input:**
- `query`: Search query
- `documents`: List of documents to search
- `top_k`: Number of results (default: 3)

**Output:**
- Ranked search results with similarity scores
- Document snippets
- Relevance rankings

---

### 5. **data_visualizer**
Create data visualizations and charts.

**Input:**
- `data`: JSON or CSV string data
- `chart_type`: 'bar', 'line', 'pie', or 'scatter'
- `x_column`, `y_column`: Column names
- `title`: Chart title

**Output:**
- Base64 encoded PNG image
- Chart dimensions
- Column information

---

### 6. **file_converter**
Convert files between formats.

**Input:**
- `input_path`: Path to input file
- `output_format`: 'txt', 'csv', or 'pdf'
- `output_path`: Optional output path

**Output:**
- Output file path
- Conversion status
- File size

**Supported Conversions:**
- PDF → TXT
- TXT → CSV
- CSV → TXT

---

### 7. **email_intent_classifier**
Classify email intent using NLP.

**Input:**
- `email_text`: Email content to classify

**Output:**
- Primary intent (inquiry, complaint, request, feedback, meeting, order, urgent, follow_up, thank_you, application)
- Confidence score
- Secondary intents

---

### 8. **kpi_generator**
Generate business KPIs and insights.

**Input:**
- `data`: JSON string with business data
- `metrics`: List of metrics - 'revenue', 'growth', 'efficiency', 'customer', 'operational'

**Output:**
- Calculated KPIs
- Executive summary
- Key trends and insights

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Setup

1. **Clone or download the repository:**

```bash
cd mission_control_mcp
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

Or using `uv`:

```bash
uv pip install -r requirements.txt
```

### Dependencies

- `mcp` - Model Context Protocol SDK
- `pypdf2` - PDF processing
- `requests` + `beautifulsoup4` - Web scraping
- `pandas` + `numpy` - Data processing
- `faiss-cpu` + `sentence-transformers` - Vector search
- `matplotlib` + `seaborn` - Data visualization
- `scikit-learn` + `nltk` - NLP and ML

---

## 🚀 Usage

### Running the Server

#### For Development/Testing:

```bash
uvx mcp dev mission_control_mcp/mcp_server.py
```

Or with Python directly:

```bash
python mcp_server.py
```

#### For Production:

The server runs via stdio and is designed to be integrated with MCP clients like Claude Desktop.

---

## 💡 Tool Examples

### Example 1: Text Extraction & Summarization

```json
{
  "tool": "text_extractor",
  "arguments": {
    "text": "Your long document text here...",
    "operation": "summarize",
    "max_length": 200
  }
}
```

### Example 2: Web Content Fetching

```json
{
  "tool": "web_fetcher",
  "arguments": {
    "url": "https://example.com/article",
    "extract_text_only": true
  }
}
```

### Example 3: Semantic Search

```json
{
  "tool": "rag_search",
  "arguments": {
    "query": "machine learning algorithms",
    "documents": [
      "Document 1 about neural networks...",
      "Document 2 about decision trees...",
      "Document 3 about clustering..."
    ],
    "top_k": 3
  }
}
```

### Example 4: Data Visualization

```json
{
  "tool": "data_visualizer",
  "arguments": {
    "data": "{\"month\": [\"Jan\", \"Feb\", \"Mar\"], \"sales\": [1000, 1500, 1200]}",
    "chart_type": "bar",
    "x_column": "month",
    "y_column": "sales",
    "title": "Q1 Sales Report"
  }
}
```

### Example 5: Email Intent Classification

```json
{
  "tool": "email_intent_classifier",
  "arguments": {
    "email_text": "Hi, I need help with my recent order. It hasn't arrived yet and I'm wondering about the tracking status."
  }
}
```

### Example 6: KPI Generation

```json
{
  "tool": "kpi_generator",
  "arguments": {
    "data": "{\"revenue\": 1000000, \"costs\": 600000, \"customers\": 500, \"current_revenue\": 1000000, \"previous_revenue\": 800000}",
    "metrics": ["revenue", "growth", "efficiency"]
  }
}
```

---

## 🖥️ Claude Desktop Integration

### Configuration

Add to your Claude Desktop config file (`claude_desktop_config.json`):

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mission-control": {
      "command": "python",
      "args": [
        "C:/Users/YourUser/path/to/mission_control_mcp/mcp_server.py"
      ]
    }
  }
}
```

Or with `uvx`:

```json
{
  "mcpServers": {
    "mission-control": {
      "command": "uvx",
      "args": [
        "mcp",
        "run",
        "C:/Users/YourUser/path/to/mission_control_mcp/mcp_server.py"
      ]
    }
  }
}
```

### Usage in Claude

After configuration, restart Claude Desktop. You can then ask Claude to:

- "Extract text from this PDF file"
- "Fetch content from this website and summarize it"
- "Search these documents for information about X"
- "Create a bar chart from this sales data"
- "Classify the intent of this email"
- "Generate KPIs from this business data"

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_server.py
```

The test suite includes:
- Text extraction and processing tests
- Web fetching tests
- RAG search demonstrations
- Data visualization generation
- Email classification examples
- KPI calculation tests
- Example JSON inputs for all tools

---

## 🏗️ Architecture

```
mission_control_mcp/
├── mcp_server.py              # Main MCP server
├── requirements.txt           # Dependencies
├── test_server.py            # Test suite
├── README.md                 # Documentation
│
├── tools/                    # Tool implementations
│   ├── pdf_reader.py
│   ├── text_extractor.py
│   ├── web_fetcher.py
│   ├── rag_search.py
│   ├── data_visualizer.py
│   ├── file_converter.py
│   ├── email_intent_classifier.py
│   └── kpi_generator.py
│
├── models/                   # Data schemas
│   └── schemas.py
│
└── utils/                    # Utilities
    ├── helpers.py            # Helper functions
    └── rag_utils.py          # RAG/vector search utilities
```

### Design Principles

- **Modularity**: Each tool is independently implemented
- **Type Safety**: Pydantic schemas for validation
- **Error Handling**: Comprehensive error catching and logging
- **Clean Code**: Well-documented with docstrings
- **Testability**: Easy to test individual components

---

## 🎖️ Hackathon Submission

### Track 1: MCP Server

**Server Name:** MissionControlMCP

**Description:** Enterprise automation MCP server providing 8 specialized tools for document processing, web intelligence, semantic search, data visualization, and business analytics.

### Key Features for Judges

1. **Production-Ready**: All 8 tools are fully implemented and tested
2. **MCP Compliant**: Follows MCP specification precisely
3. **Real-World Value**: Solves actual enterprise automation needs
4. **Clean Architecture**: Modular, maintainable, well-documented code
5. **Advanced Features**: RAG search with FAISS, data visualization, NLP classification
6. **Comprehensive Testing**: Full test suite with examples
7. **Easy Integration**: Works seamlessly with Claude Desktop

### Technical Highlights

- **Vector Search**: FAISS-based semantic search with sentence transformers
- **NLP Classification**: Rule-based email intent classifier with confidence scoring
- **Data Visualization**: Dynamic chart generation with matplotlib
- **File Processing**: Multi-format support (PDF, TXT, CSV)
- **Web Intelligence**: Smart web scraping with clean text extraction
- **Business Intelligence**: KPI calculation with trend analysis

---

## 📝 License

This project is created for the MCP 1st Birthday Hackathon – Winter 2025.

---

## 🤝 Contributing

This project was built for the hackathon, but improvements and suggestions are welcome!

---

## 📧 Contact

For questions about this MCP server, please reach out through the hackathon channels.

---

## 🌟 Acknowledgments

- Built with the [Model Context Protocol SDK](https://github.com/modelcontextprotocol)
- Powered by sentence-transformers, FAISS, and other open-source libraries
- Created for the MCP 1st Birthday Hackathon 2025

---

**Happy Automating! 🚀**
