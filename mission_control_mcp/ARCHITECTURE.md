# 🏗️ System Architecture

MissionControlMCP system design and architecture documentation.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Claude       │  │  Custom      │  │  Other MCP   │      │
│  │ Desktop      │  │  Client      │  │  Clients     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │ MCP Protocol (stdio)
┌──────────────────────┴──────────────────────────────────────┐
│                    MCP Server Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              mcp_server.py                             │ │
│  │  • Tool Registration                                   │ │
│  │  • Request Routing                                     │ │
│  │  • Response Formatting                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │ PDF      │ Text     │ Web      │ RAG      │            │
│  │ Reader   │ Extract  │ Fetcher  │ Search   │            │
│  ├──────────┼──────────┼──────────┼──────────┤            │
│  │ Data     │ File     │ Email    │ KPI      │            │
│  │ Visual   │ Convert  │ Classify │ Generate │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    Utility Layer                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • helpers.py      - Text processing utilities         │ │
│  │  • rag_utils.py    - Vector search & FAISS             │ │
│  │  • schemas.py      - Pydantic models                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Architecture

### 1. MCP Server (`mcp_server.py`)

**Responsibilities:**
- Register all 8 tools with MCP SDK
- Handle incoming tool requests
- Route requests to appropriate tool functions
- Format and return responses
- Error handling and logging

**Flow:**
```
Client Request → MCP Protocol → Server → Tool → Response → Client
```

**Code Structure:**
```python
# Tool Registration
server.register_tool(name, description, input_schema)

# Request Handler
async def call_tool(name, arguments):
    if name == "pdf_reader":
        return await pdf_reader.read_pdf(**arguments)
    elif name == "text_extractor":
        return await text_extractor.extract_text(**arguments)
    # ... other tools

# Server Startup
async with stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream)
```

---

### 2. Tool Layer (`tools/`)

Each tool is independent and follows this pattern:

**Tool Structure:**
```python
"""
Tool Name - Description
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def tool_function(param: str) -> Dict[str, Any]:
    """
    Tool description.
    
    Args:
        param: Parameter description
        
    Returns:
        Standardized result dictionary
    """
    try:
        # Validation
        if not param:
            raise ValueError("Invalid input")
        
        # Processing
        result = process_data(param)
        
        # Return standardized format
        return {
            "success": True,
            "data": result,
            "metadata": {}
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

**Tool Independence:**
- Each tool is self-contained
- No dependencies between tools
- Can be tested individually
- Easy to add/remove tools

---

### 3. Utility Layer (`utils/`)

**helpers.py - Text Processing:**
```python
• clean_text() - Remove extra whitespace
• extract_keywords() - NLP keyword extraction
• chunk_text() - Text splitting with overlap
• validate_url() - URL validation
```

**rag_utils.py - Vector Search:**
```python
• SimpleRAGStore - FAISS-based vector database
• semantic_search() - Sentence transformer embeddings
• create_rag_store() - Initialize vector store
```

**Models (models/schemas.py):**
```python
• Pydantic models for type validation
• Input/output schemas
• Data validation
```

---

## 🔄 Data Flow

### Request Flow

```
1. Client sends MCP request
   ↓
2. mcp_server.py receives request
   ↓
3. Server validates input schema
   ↓
4. Server routes to tool function
   ↓
5. Tool processes data
   ↓
6. Tool returns result dict
   ↓
7. Server formats MCP response
   ↓
8. Client receives response
```

### Example: PDF Reading Flow

```
Client: "Read this PDF"
   ↓
MCP Server: Receives pdf_reader request
   ↓
pdf_reader.py: read_pdf(file_path)
   ↓
PyPDF2: Extract text from pages
   ↓
Return: {text, pages, metadata}
   ↓
MCP Server: Format response
   ↓
Client: Receives extracted text
```

---

## 🗂️ Project Structure

```
mission_control_mcp/
│
├── mcp_server.py              # MCP server entry point
│
├── tools/                     # 8 independent tools
│   ├── pdf_reader.py          # PDF text extraction
│   ├── text_extractor.py      # Text processing (4 ops)
│   ├── web_fetcher.py         # Web scraping
│   ├── rag_search.py          # Semantic search
│   ├── data_visualizer.py     # Chart generation
│   ├── file_converter.py      # File format conversion
│   ├── email_intent_classifier.py  # Email classification
│   └── kpi_generator.py       # Business metrics
│
├── utils/                     # Shared utilities
│   ├── helpers.py             # Text processing helpers
│   └── rag_utils.py           # Vector search utilities
│
├── models/                    # Data models
│   └── schemas.py             # Pydantic schemas
│
├── examples/                  # Sample test data
│   ├── sample_report.txt      # Business report
│   ├── business_data.csv      # Financial data
│   ├── sample_email_*.txt     # Email samples
│   └── sample_documents.txt   # RAG search docs
│
├── app.py                     # Gradio web interface
├── demo.py                    # Demo & test suite
│
├── docs/                      # Documentation
│   ├── README.md              # Main documentation
│   ├── API.md                 # API reference
│   ├── EXAMPLES.md            # Use cases
│   ├── TESTING.md             # Testing guide
│   ├── ARCHITECTURE.md        # This file
│   └── CONTRIBUTING.md        # Contribution guide
│
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── LICENSE                    # MIT License
```

---

## 🔌 Integration Points

### MCP Protocol Integration

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

# Create server
server = Server("mission-control")

# Register tool
@server.tool()
async def pdf_reader(file_path: str) -> str:
    result = read_pdf(file_path)
    return json.dumps(result)

# Run server
await server.run(stdin, stdout)
```

### Claude Desktop Integration

**Configuration:**
```json
{
  "mcpServers": {
    "mission-control": {
      "command": "python",
      "args": ["path/to/mcp_server.py"]
    }
  }
}
```

**Communication:**
```
Claude Desktop ←→ MCP Protocol ←→ mcp_server.py ←→ Tools
```

---

## 🚀 Scalability Design

### Horizontal Scaling

**Current:** Single-process server
**Future:** Multi-process with load balancing

```
             Load Balancer
                   │
        ┌──────────┼──────────┐
        │          │          │
   Server 1    Server 2    Server 3
        │          │          │
        └──────────┴──────────┘
                Tools
```

### Caching Strategy

**Implemented:**
- RAG model caching (sentence transformers)
- NLTK data caching

**Future Improvements:**
- Redis for result caching
- Database for document storage
- CDN for static assets

---

## 🔒 Security Architecture

### Input Validation

```python
# Pydantic schemas
from pydantic import BaseModel, validator

class PDFReaderInput(BaseModel):
    file_path: str
    
    @validator('file_path')
    def validate_path(cls, v):
        if not Path(v).exists():
            raise ValueError("File not found")
        return v
```

### Error Handling

```python
try:
    result = tool_function(input)
except FileNotFoundError:
    return {"error": "File not found", "code": 404}
except ValueError:
    return {"error": "Invalid input", "code": 400}
except Exception:
    return {"error": "Internal error", "code": 500}
```

### Authentication

**Current:** None (local tool execution)
**Production Considerations:**
- API key authentication
- Rate limiting
- Request logging
- User permissions

---

## 📊 Performance Characteristics

### Tool Performance

| Tool | Avg Time | Memory | Notes |
|------|----------|--------|-------|
| PDF Reader | 1s | 50MB | Depends on PDF size |
| Text Extractor | 0.5s | 10MB | Fast text processing |
| Web Fetcher | 2-3s | 20MB | Network dependent |
| RAG Search | 2.5s* | 200MB | *First run (model load) |
| RAG Search | 0.5s | 200MB | Subsequent runs |
| Data Visualizer | 1.2s | 30MB | Chart generation |
| File Converter | 1-2s | 50MB | File size dependent |
| Email Classifier | 0.1s | 5MB | Very fast |
| KPI Generator | 0.3s | 10MB | Quick calculations |

### Bottlenecks

1. **RAG Search** - Initial model loading (~2s)
   - Solution: Keep model in memory
   
2. **Web Fetcher** - Network latency
   - Solution: Async requests, caching
   
3. **PDF Reader** - Large files
   - Solution: Stream processing

---

## 🔄 State Management

### Stateless Design

Each tool request is independent:
- No session state
- No user context
- Pure function design

**Benefits:**
- Easy scaling
- No state synchronization
- Simple debugging
- High availability

### RAG Store State

Exception: RAG search maintains in-memory vector store:
```python
class SimpleRAGStore:
    def __init__(self):
        self.documents = []
        self.index = None  # FAISS index
```

**Lifecycle:**
- Created on first search
- Persists during server lifetime
- Cleared on server restart

---

## 🧪 Testing Architecture

### Test Pyramid

```
         ┌─────────────┐
         │   E2E Tests │  (MCP integration)
         ├─────────────┤
         │ Integration │  (Tool combinations)
         ├─────────────┤
         │  Unit Tests │  (Individual functions)
         └─────────────┘
```

### Test Coverage

- **Unit Tests:** Test each function independently
- **Integration Tests:** Test tool interactions
- **MCP Tests:** Test server communication
- **Sample Tests:** Test with real data

---

## 📦 Dependency Management

### Core Dependencies

```
MCP SDK (>=1.0.0)
├── stdio communication
└── Tool registration

Processing Libraries
├── PyPDF2 (PDF reading)
├── BeautifulSoup4 (HTML parsing)
├── Pandas (Data processing)
└── Matplotlib (Visualization)

ML/NLP Libraries
├── scikit-learn (Text processing)
├── NLTK (Keyword extraction)
├── sentence-transformers (Embeddings)
└── FAISS (Vector search)
```

### Optional Dependencies

- faiss-cpu: Can use faiss-gpu on GPU systems
- reportlab: Optional for PDF generation

---

## 🔮 Future Architecture Improvements

### Planned Enhancements

1. **Database Integration**
   ```
   PostgreSQL for persistent storage
   Redis for caching
   ```

2. **Async Processing**
   ```python
   async def process_pdf(file_path: str):
       # Async PDF processing
       return await asyncio.to_thread(read_pdf, file_path)
   ```

3. **Microservices**
   ```
   Each tool as separate service
   API gateway for routing
   Service mesh for communication
   ```

4. **Monitoring**
   ```
   Prometheus metrics
   Grafana dashboards
   Error tracking (Sentry)
   ```

---

## 📝 Design Principles

### SOLID Principles

- **Single Responsibility:** Each tool does one thing
- **Open/Closed:** Easy to add new tools
- **Liskov Substitution:** Tools are interchangeable
- **Interface Segregation:** Minimal tool interfaces
- **Dependency Inversion:** Tools depend on abstractions

### Clean Architecture

- **Independent of Frameworks:** Core logic separate from MCP
- **Testable:** Can test without MCP server
- **Independent of UI:** Works with any MCP client
- **Independent of Database:** No database coupling

---

## 🎯 Architectural Goals

✅ **Achieved:**
- Modular design
- Easy to extend
- Well-documented
- Testable
- Production-ready

🔄 **In Progress:**
- Performance optimization
- Enhanced caching
- Better error handling

🎯 **Future:**
- Multi-tenancy
- Distributed processing
- Advanced monitoring
- Auto-scaling

---

**MissionControlMCP Architecture Documentation v1.0** 🏗️
