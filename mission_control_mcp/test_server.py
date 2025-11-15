"""
Test script for MissionControlMCP server
Tests all tools with example inputs
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.pdf_reader import read_pdf
from tools.text_extractor import extract_text
from tools.web_fetcher import fetch_web_content
from tools.rag_search import search_documents
from tools.data_visualizer import visualize_data
from tools.file_converter import convert_file
from tools.email_intent_classifier import classify_email_intent
from tools.kpi_generator import generate_kpis


def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_text_extractor():
    """Test text extraction tool"""
    print_section("Testing Text Extractor")
    
    sample_text = """
    This is a sample document with multiple sentences. It contains information 
    about various topics including technology, business, and innovation. 
    The text is meant to demonstrate the capabilities of text processing 
    tools in the MissionControlMCP server. These tools can clean text, 
    summarize content, extract keywords, and chunk large documents into 
    manageable pieces for further processing.
    """
    
    try:
        # Test clean operation
        print("\n1. Clean operation:")
        result = extract_text(sample_text, operation="clean")
        print(f"   Word count: {result['word_count']}")
        print(f"   Result preview: {result['result'][:100]}...")
        
        # Test summarize operation
        print("\n2. Summarize operation:")
        result = extract_text(sample_text, operation="summarize", max_length=100)
        print(f"   Summary: {result['result']}")
        
        # Test keywords operation
        print("\n3. Keywords operation:")
        result = extract_text(sample_text, operation="keywords")
        print(f"   Keywords: {result['result']}")
        
        print("\n✓ Text Extractor tests passed")
    except Exception as e:
        print(f"\n✗ Text Extractor test failed: {e}")


def test_web_fetcher():
    """Test web fetcher tool"""
    print_section("Testing Web Fetcher")
    
    test_url = "https://example.com"
    
    try:
        print(f"\nFetching content from: {test_url}")
        result = fetch_web_content(test_url, extract_text_only=True)
        print(f"   Status code: {result['status_code']}")
        print(f"   Content length: {len(result['content'])} characters")
        print(f"   Content preview: {result['content'][:150]}...")
        print("\n✓ Web Fetcher test passed")
    except Exception as e:
        print(f"\n✗ Web Fetcher test failed: {e}")


def test_rag_search():
    """Test RAG search tool"""
    print_section("Testing RAG Search")
    
    documents = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        "Data science involves extracting insights from structured and unstructured data.",
        "Cloud computing provides on-demand access to computing resources over the internet.",
        "Cybersecurity protects systems and networks from digital attacks and threats."
    ]
    
    query = "What is machine learning?"
    
    try:
        print(f"\nQuery: {query}")
        print(f"Searching in {len(documents)} documents...")
        result = search_documents(query, documents, top_k=3)
        
        print(f"\nFound {result['returned_results']} results:")
        for item in result['results']:
            print(f"\n   Rank {item['rank']} (score: {item['score']}):")
            print(f"   {item['document'][:80]}...")
        
        print("\n✓ RAG Search test passed")
    except Exception as e:
        print(f"\n✗ RAG Search test failed: {e}")


def test_data_visualizer():
    """Test data visualizer tool"""
    print_section("Testing Data Visualizer")
    
    # Sample data
    data = json.dumps({
        "month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "sales": [1200, 1500, 1300, 1800, 2000]
    })
    
    try:
        print("\nCreating bar chart from sales data...")
        result = visualize_data(
            data=data,
            chart_type="bar",
            x_column="month",
            y_column="sales",
            title="Monthly Sales"
        )
        
        print(f"   Chart created: {result['chart_type']}")
        print(f"   Dimensions: {result['dimensions']}")
        print(f"   Image size: {len(result['image_base64'])} characters (base64)")
        print("\n✓ Data Visualizer test passed")
    except Exception as e:
        print(f"\n✗ Data Visualizer test failed: {e}")


def test_email_classifier():
    """Test email intent classifier"""
    print_section("Testing Email Intent Classifier")
    
    test_emails = [
        {
            "label": "Inquiry",
            "text": "Hi, I have a question about your product pricing. Could you please provide more information about the enterprise plan?"
        },
        {
            "label": "Complaint",
            "text": "I'm very disappointed with the service. The product stopped working and I haven't received any support."
        },
        {
            "label": "Meeting Request",
            "text": "Would you be available for a call next week to discuss the project details? I'm free Tuesday afternoon."
        }
    ]
    
    try:
        for email in test_emails:
            print(f"\n{email['label']} Email:")
            result = classify_email_intent(email['text'])
            print(f"   Detected intent: {result['intent']}")
            print(f"   Confidence: {result['confidence']}")
            if result['secondary_intents']:
                print(f"   Secondary: {result['secondary_intents'][0]['intent']} ({result['secondary_intents'][0]['confidence']})")
        
        print("\n✓ Email Classifier test passed")
    except Exception as e:
        print(f"\n✗ Email Classifier test failed: {e}")


def test_kpi_generator():
    """Test KPI generator tool"""
    print_section("Testing KPI Generator")
    
    business_data = json.dumps({
        "revenue": 1000000,
        "costs": 600000,
        "customers": 500,
        "current_revenue": 1000000,
        "previous_revenue": 800000,
        "current_customers": 500,
        "previous_customers": 400,
        "employees": 50
    })
    
    try:
        print("\nGenerating KPIs from business data...")
        result = generate_kpis(business_data, metrics=["revenue", "growth", "efficiency"])
        
        print("\nCalculated KPIs:")
        for key, value in list(result['kpis'].items())[:5]:
            if isinstance(value, (int, float)):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        
        print(f"\nSummary:")
        print(f"   {result['summary']}")
        
        print(f"\nTrends:")
        for trend in result['trends']:
            print(f"   • {trend}")
        
        print("\n✓ KPI Generator test passed")
    except Exception as e:
        print(f"\n✗ KPI Generator test failed: {e}")


def test_file_operations():
    """Test file converter (limited test without actual files)"""
    print_section("Testing File Operations")
    
    print("\nFile Converter:")
    print("   Supports: PDF ↔ TXT, TXT ↔ CSV")
    print("   (Skipping file I/O tests - requires actual files)")
    print("\nPDF Reader:")
    print("   Extracts text and metadata from PDF files")
    print("   (Skipping file I/O tests - requires actual PDF files)")
    print("\n✓ File operations tools available")


def run_all_tests():
    """Run all tests"""
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*15 + "MissionControlMCP Test Suite" + " "*15 + "║")
    print("╚" + "═"*58 + "╝")
    
    test_text_extractor()
    test_web_fetcher()
    test_rag_search()
    test_data_visualizer()
    test_email_classifier()
    test_kpi_generator()
    test_file_operations()
    
    print("\n" + "="*60)
    print("  Test Suite Complete!")
    print("="*60 + "\n")
    
    print("📝 Example JSON Inputs for Each Tool:\n")
    
    examples = {
        "pdf_reader": {
            "file_path": "/path/to/document.pdf"
        },
        "text_extractor": {
            "text": "Your text here...",
            "operation": "summarize",
            "max_length": 500
        },
        "web_fetcher": {
            "url": "https://example.com",
            "extract_text_only": True
        },
        "rag_search": {
            "query": "machine learning",
            "documents": ["doc1", "doc2", "doc3"],
            "top_k": 3
        },
        "data_visualizer": {
            "data": '{"x": [1,2,3], "y": [4,5,6]}',
            "chart_type": "bar",
            "title": "My Chart"
        },
        "file_converter": {
            "input_path": "/path/to/input.pdf",
            "output_format": "txt"
        },
        "email_intent_classifier": {
            "email_text": "I need help with my order..."
        },
        "kpi_generator": {
            "data": '{"revenue": 100000, "costs": 60000}',
            "metrics": ["revenue", "growth"]
        }
    }
    
    for tool_name, example_input in examples.items():
        print(f"\n{tool_name}:")
        print(json.dumps(example_input, indent=2))


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
