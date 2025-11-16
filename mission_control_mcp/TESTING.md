# 🧪 Testing Guide

## Quick Start: Test with Sample Files

We've created sample files in the `examples/` directory to demonstrate all MissionControlMCP tools.

### Run All Tests

```bash
python demo.py
```

This will test:
- ✅ **Text Extraction** - Keywords & summarization from business report
- ✅ **Email Classification** - Intent detection on 3 sample emails  
- ✅ **Data Visualization** - Line and bar charts from CSV data
- ✅ **KPI Generation** - Calculate business metrics
- ✅ **RAG Semantic Search** - Semantic search across documents

---

## Test Individual Tools

### 1. Text Extractor
```python
from tools.text_extractor import extract_text

# Read sample report
with open("examples/sample_report.txt", "r") as f:
    text = f.read()

# Extract keywords
keywords = extract_text(text, operation="keywords")
print(keywords)

# Generate summary
summary = extract_text(text, operation="summarize", max_length=200)
print(summary['result'])
```

### 2. Email Intent Classifier
```python
from tools.email_intent_classifier import classify_email_intent

# Test complaint email
with open("examples/sample_email_complaint.txt", "r") as f:
    email = f.read()

result = classify_email_intent(email)
print(f"Intent: {result['intent']} (confidence: {result['confidence']})")
```

### 3. Data Visualizer
```python
from tools.data_visualizer import visualize_data

# Load CSV data
with open("examples/business_data.csv", "r") as f:
    data = f.read()

# Create revenue trend chart
chart = visualize_data(
    data=data,
    chart_type="line",
    x_column="month",
    y_column="revenue",
    title="Revenue Trends"
)

# Save chart
import base64
with open("revenue_chart.png", "wb") as f:
    f.write(base64.b64decode(chart['image_base64']))
```

### 4. KPI Generator
```python
from tools.kpi_generator import generate_kpis
import json

data = {
    "revenue": 5500000,
    "costs": 3400000,
    "customers": 2700,
    "current_revenue": 5500000,
    "previous_revenue": 5400000,
    "employees": 50
}

result = generate_kpis(json.dumps(data), metrics=["revenue", "growth", "efficiency"])
print(f"Generated {len(result['kpis'])} KPIs")
print(result['summary'])
```

### 5. RAG Semantic Search
```python
from tools.rag_search import search_documents

# Load sample documents
with open("examples/sample_documents.txt", "r") as f:
    content = f.read()

documents = [doc.strip() for doc in content.split("##") if doc.strip()]

# Search
results = search_documents("What is machine learning?", documents, top_k=3)
for res in results['results']:
    print(f"Score: {res['score']:.4f} - {res['document'][:100]}...")
```

---

## Test with Claude Desktop

### 1. Configure Claude Desktop

Edit `%AppData%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mission-control": {
      "command": "python",
      "args": ["C:/path/to/mission_control_mcp/mcp_server.py"]
    }
  }
}
```

### 2. Restart Claude Desktop

### 3. Try These Prompts

**Text Processing:**
```
Extract keywords from this text: [paste sample_report.txt content]
```

**Email Classification:**
```
Classify this email: [paste sample_email_complaint.txt content]
```

**Data Visualization:**
```
Create a line chart showing revenue trends from this data: [paste business_data.csv]
```

**KPI Generation:**
```
Calculate KPIs from this business data: {"revenue": 5000000, "costs": 3000000, "customers": 2500}
```

**Semantic Search:**
```
Search these documents for information about AI: [paste sample_documents.txt]
```

---

## Test MCP Server Directly

### Run the MCP Server

```bash
python mcp_server.py
```

### Test Individual Tools

```bash
python test_individual.py
```

This runs isolated tests on each tool (8 total).

### MCP Server Tests

```bash
python demo.py
```

Tests all MCP tool handlers and server integration.

---

## Sample Files Overview

| File | Purpose | Tool |
|------|---------|------|
| `sample_report.txt` | Business report (2,200 chars) | Text Extractor |
| `business_data.csv` | 12 months financial data | Data Visualizer, KPI Generator |
| `sample_email_complaint.txt` | Customer complaint | Email Classifier |
| `sample_email_inquiry.txt` | Sales inquiry | Email Classifier |
| `sample_email_urgent.txt` | Urgent system alert | Email Classifier |
| `sample_documents.txt` | 5 topic documents | RAG Search |

---

## Expected Results

### Text Extraction
- **Keywords:** customer, revenue, growth, operational, market, performance
- **Summary:** ~200 character executive summary

### Email Classification
- **Complaint:** request + order intents (confidence: 1.00)
- **Inquiry:** meeting + inquiry intents (confidence: 1.00)
- **Urgent:** urgent intent (confidence: 1.00)

### Data Visualization
- **Line Chart:** 48KB base64 PNG (1000x600px)
- **Bar Chart:** 26KB base64 PNG (1000x600px)

### KPI Generation
- **9 KPIs calculated:** total_revenue, profit, profit_margin_percent, revenue_growth, etc.
- **Summary:** Executive insights on revenue growth and profitability

### RAG Search
- **Query:** "What is machine learning?"
- **Top Result:** Document 1 (AI Overview) - Score: 0.56
- **Semantic matching:** Finds relevant content even with different wording

---

## Troubleshooting

### FAISS Errors
```bash
pip install faiss-cpu sentence-transformers
```

### Import Errors
```bash
cd mission_control_mcp
pip install -r requirements.txt
```

### Python Version
Requires Python 3.11+. Check with:
```bash
python --version
```

---

## Performance Benchmarks

| Tool | Sample File | Execution Time |
|------|-------------|----------------|
| Text Extractor | 2,200 chars | ~0.5s |
| Email Classifier | 500 chars | ~0.1s |
| Data Visualizer | 12 data points | ~1.2s |
| KPI Generator | 10 metrics | ~0.3s |
| RAG Search | 6 documents | ~2.5s (first run, includes model load) |

---

## Next Steps

1. ✅ Run `python demo.py` to verify all tools work
2. ✅ Try individual tool tests with your own data
3. ✅ Configure Claude Desktop integration
4. ✅ Test with Claude using sample prompts
5. ✅ Create custom workflows combining multiple tools

**Happy Testing!** 🚀
