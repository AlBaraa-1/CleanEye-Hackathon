"""
🚀 MissionControlMCP - Gradio Web Interface
Beautiful GUI demo for all 8 tools!

Run: python demo_gui.py
Then share the public URL on LinkedIn!
"""

import gradio as gr
import sys
import os
import json
import base64
from io import BytesIO
from PIL import Image

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
EXAMPLES_DIR = os.path.join(SCRIPT_DIR, "examples")

# Import tools
from tools.pdf_reader import read_pdf
from tools.text_extractor import extract_text
from tools.web_fetcher import fetch_web_content
from tools.rag_search import search_documents
from tools.data_visualizer import visualize_data
from tools.file_converter import convert_file
from tools.email_intent_classifier import classify_email_intent
from tools.kpi_generator import generate_kpis


# ============================================================================
# TOOL FUNCTIONS
# ============================================================================

def tool_pdf_reader(pdf_file):
    """PDF Reader tool"""
    try:
        if pdf_file is None:
            return "❌ Please upload a PDF file!", None
        
        result = read_pdf(pdf_file.name)
        
        output = f"""✅ **PDF Analysis Complete!**

📄 **Metadata:**
- Pages: {result['pages']}
- Characters: {len(result['text']):,}
- Author: {result['metadata'].get('author', 'N/A')}
- Title: {result['metadata'].get('title', 'N/A')}

📝 **Extracted Text (first 1000 chars):**
{result['text'][:1000]}...
"""
        
        # Extract keywords
        keywords = extract_text(result['text'], operation="keywords")
        output += f"\n\n🔑 **Keywords:** {keywords['result']}"
        
        return output, None
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None


def tool_text_extractor(text, operation, max_length):
    """Text Extractor tool"""
    try:
        if not text.strip():
            return "❌ Please enter some text!"
        
        result = extract_text(text, operation=operation, max_length=max_length)
        
        output = f"""✅ **Text Processing Complete!**

📊 **Operation:** {operation.upper()}
📏 **Word Count:** {result['word_count']}

📝 **Result:**
{result['result']}
"""
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


def tool_web_fetcher(url):
    """Web Fetcher tool"""
    try:
        if not url.strip():
            return "❌ Please enter a URL!"
        
        result = fetch_web_content(url)
        
        if result['status_code'] == 999:
            return f"""⚠️ **Status 999 - Bot Detection**

The website is blocking automated requests.
This is common for LinkedIn, Facebook, etc.

Try a different website!"""
        
        output = f"""✅ **Website Fetched Successfully!**

🌐 **URL:** {url}
📊 **Status:** {result['status_code']}
📄 **Title:** {result.get('title', 'N/A')}
📏 **Content Length:** {len(result['content']):,} characters
🔗 **Links Found:** {len(result.get('links', []))}

📝 **Content Preview (first 1000 chars):**
{result['content'][:1000]}...
"""
        
        # Extract keywords
        if len(result['content']) > 50:
            keywords = extract_text(result['content'], operation="keywords")
            output += f"\n\n🔑 **Keywords:** {keywords['result']}"
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


def tool_rag_search(query):
    """RAG Search tool"""
    try:
        if not query.strip():
            return "❌ Please enter a search query!"
        
        # Load sample documents
        docs_file = os.path.join(EXAMPLES_DIR, "sample_documents.txt")
        with open(docs_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        documents = [doc.strip() for doc in content.split("##") if doc.strip()]
        
        result = search_documents(query, documents, top_k=3)
        
        output = f"""✅ **Search Complete!**

🔍 **Query:** "{query}"
📚 **Documents Searched:** {len(documents)}
📊 **Results Found:** {len(result['results'])}

🎯 **Top Results:**

"""
        
        for i, res in enumerate(result['results'], 1):
            preview = res['document'][:200].replace('\n', ' ')
            output += f"""
**Result {i}** (Score: {res['score']:.4f})
{preview}...

"""
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


def tool_data_visualizer(csv_data, chart_type, x_col, y_col, title):
    """Data Visualizer tool"""
    try:
        if not csv_data.strip():
            return "❌ Please enter CSV data!", None
        
        result = visualize_data(
            data=csv_data,
            chart_type=chart_type,
            x_column=x_col,
            y_column=y_col,
            title=title
        )
        
        # Convert base64 to image
        img_data = base64.b64decode(result['image_base64'])
        image = Image.open(BytesIO(img_data))
        
        output = f"""✅ **Chart Created!**

📊 **Chart Type:** {chart_type.upper()}
📏 **Dimensions:** {result['dimensions']}
📈 **Title:** {title}
"""
        
        return output, image
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None


def tool_email_classifier(email_text):
    """Email Intent Classifier tool"""
    try:
        if not email_text.strip():
            return "❌ Please enter email text!"
        
        result = classify_email_intent(email_text)
        
        output = f"""✅ **Email Classified!**

🎯 **Primary Intent:** {result['intent'].upper()}
📊 **Confidence:** {result['confidence']:.2%}

💬 **Explanation:**
{result['explanation']}
"""
        
        if result['secondary_intents']:
            output += "\n\n📋 **Secondary Intents:**\n"
            for intent in result['secondary_intents'][:3]:
                output += f"- {intent['intent']}: {intent['confidence']:.2%}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


def tool_kpi_generator(business_json, metrics):
    """KPI Generator tool"""
    try:
        if not business_json.strip():
            return "❌ Please enter business data!"
        
        # Validate JSON
        json.loads(business_json)
        
        result = generate_kpis(business_json, metrics=metrics)
        
        output = f"""✅ **KPIs Generated!**

📊 **Total KPIs Calculated:** {len(result['kpis'])}

📈 **Key Metrics:**

"""
        
        # Display top 15 KPIs
        for i, (name, value) in enumerate(list(result['kpis'].items())[:15], 1):
            # Format based on metric type
            if 'percent' in name or 'rate' in name or 'margin' in name:
                formatted = f"{value:.1f}%"
            elif 'revenue' in name or 'profit' in name or 'cost' in name:
                formatted = f"${value:,.0f}"
            else:
                formatted = f"{value:,.2f}"
            
            display_name = name.replace('_', ' ').title()
            output += f"{i}. **{display_name}:** {formatted}\n"
        
        output += f"\n\n📝 **Executive Summary:**\n{result['summary']}"
        
        if result.get('trends'):
            output += "\n\n📊 **Key Trends:**\n"
            for trend in result['trends'][:5]:
                output += f"- {trend}\n"
        
        return output
        
    except json.JSONDecodeError:
        return "❌ Invalid JSON format! Please check your data."
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ============================================================================
# LOAD SAMPLE DATA
# ============================================================================

def load_sample_csv():
    csv_file = os.path.join(EXAMPLES_DIR, "business_data.csv")
    with open(csv_file, "r") as f:
        return f.read()

def load_sample_email():
    email_file = os.path.join(EXAMPLES_DIR, "sample_email_complaint.txt")
    with open(email_file, "r", encoding="utf-8") as f:
        return f.read()

def load_sample_json():
    return """{
    "revenue": 5500000,
    "costs": 3400000,
    "customers": 2700,
    "current_revenue": 5500000,
    "previous_revenue": 5400000,
    "current_customers": 2700,
    "previous_customers": 2650,
    "employees": 50,
    "marketing_spend": 500000,
    "sales": 5500000,
    "cogs": 2000000
}"""


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

# Custom CSS for beautiful UI
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.gradio-container {
    font-family: 'Inter', sans-serif !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
}

/* Header styling */
.gradio-container h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3em !important;
    font-weight: 700 !important;
    text-align: center;
    margin-bottom: 0.5em;
}

/* Tab styling */
.tab-nav {
    border-radius: 12px !important;
    background: linear-gradient(to right, #f8f9fa, #e9ecef) !important;
    padding: 8px !important;
    margin-bottom: 20px !important;
}

button.selected {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

/* Button styling */
.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
}

/* Input fields */
textarea, input[type="text"] {
    border-radius: 10px !important;
    border: 2px solid #e9ecef !important;
    padding: 12px !important;
    font-size: 15px !important;
    transition: border-color 0.3s ease !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Output boxes */
.output-class {
    background: linear-gradient(to bottom, #ffffff, #f8f9fa) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    border: 2px solid #e9ecef !important;
}

/* Cards and containers */
.gr-box {
    border-radius: 12px !important;
    border: 1px solid #e9ecef !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

/* Labels */
label {
    font-weight: 600 !important;
    color: #495057 !important;
    font-size: 14px !important;
    margin-bottom: 8px !important;
}

/* Examples */
.gr-samples-table {
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px;
    background: linear-gradient(to right, #f8f9fa, #e9ecef);
    border-radius: 12px;
    margin-top: 30px;
}

/* Image display */
.gr-image {
    border-radius: 12px !important;
    border: 2px solid #e9ecef !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
}

/* Radio buttons and checkboxes */
.gr-radio, .gr-checkbox {
    padding: 10px !important;
    border-radius: 8px !important;
}

/* File upload */
.gr-file {
    border: 2px dashed #667eea !important;
    border-radius: 12px !important;
    background: linear-gradient(to bottom, #ffffff, #f8f9fa) !important;
    padding: 30px !important;
}

.gr-file:hover {
    border-color: #764ba2 !important;
    background: #f8f9fa !important;
}
"""

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="MissionControlMCP Demo") as demo:
    
    gr.Markdown("# 🚀 MissionControlMCP")
    gr.Markdown("### Enterprise Automation Tools - Powered by AI")
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 30px;">
        <h3 style="color: white; margin: 0;">✨ Try all 8 powerful tools in your browser - No installation needed! ✨</h3>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Built for HuggingFace Gradio Hackathon | Claude MCP Integration</p>
    </div>
    """)
    
    with gr.Tabs():
        
        # ====== TAB 1: PDF READER ======
        with gr.Tab("📄 PDF Reader"):
            gr.Markdown("""
            ### 📄 Extract Text and Metadata from PDF Documents
            Upload any PDF file to extract its content, metadata, and keywords instantly.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(
                        label="📎 Upload PDF File",
                        file_types=[".pdf"],
                        elem_classes=["file-upload"]
                    )
                    pdf_btn = gr.Button(
                        "🔍 Extract Text from PDF",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                    gr.Markdown("""
                    **💡 Tips:**
                    - Supports multi-page PDFs
                    - Extracts metadata (author, title)
                    - Automatically generates keywords
                    
                    **⚠️ Limitations:**
                    - Max file size: 200 MB (HuggingFace limit)
                    - Text-based PDFs only (scanned images need OCR)
                    - Processing time: ~2-5 seconds per page
                    """)
                
                with gr.Column(scale=2):
                    pdf_output = gr.Textbox(
                        label="📊 Extraction Results",
                        lines=20,
                        elem_classes=["output-class"]
                    )
                    pdf_img = gr.Image(label="Preview", visible=False)
            
            pdf_btn.click(tool_pdf_reader, inputs=[pdf_input], outputs=[pdf_output, pdf_img])
            
            gr.Markdown("*💡 Try uploading your resume, research paper, or any PDF document!*")
        
        # ====== TAB 2: TEXT EXTRACTOR ======
        with gr.Tab("📝 Text Extractor"):
            gr.Markdown("""
            ### 📝 AI-Powered Text Analysis
            Extract keywords, generate summaries, clean text, or split into chunks.
            
            **⚠️ Limitations:**
            - Max input: ~50,000 characters
            - Summary length: 100-1000 characters (adjustable)
            - Processing time: ~1-3 seconds
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    text_input = gr.Textbox(
                        label="✍️ Enter Your Text", 
                        lines=10,
                        placeholder="Paste any text here - articles, reports, emails, etc...",
                        elem_classes=["input-field"]
                    )
                    text_operation = gr.Radio(
                        ["keywords", "summarize", "clean", "chunk"],
                        label="🛠️ Select Operation",
                        value="keywords",
                        info="Choose what to do with your text"
                    )
                    text_length = gr.Slider(
                        100, 1000, 300,
                        label="📏 Max Length (for summarize/chunk)",
                        info="Adjust output length"
                    )
                    text_btn = gr.Button(
                        "✨ Process Text",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                
                with gr.Column(scale=2):
                    text_output = gr.Textbox(
                        label="📊 Processing Results",
                        lines=20,
                        elem_classes=["output-class"]
                    )
            
            text_btn.click(
                tool_text_extractor,
                inputs=[text_input, text_operation, text_length],
                outputs=[text_output]
            )
            
            gr.Examples([
                ["Artificial Intelligence is transforming businesses worldwide. Companies are leveraging AI for automation, decision-making, and customer service. Machine learning models can now process vast amounts of data and provide actionable insights.", "keywords", 300],
                ["Climate change is one of the most pressing challenges of our time. Rising temperatures, extreme weather events, and environmental degradation require urgent action.", "summarize", 300]
            ], inputs=[text_input, text_operation, text_length], label="📚 Try These Examples")
        
        # ====== TAB 3: WEB FETCHER ======
        with gr.Tab("🌐 Web Fetcher"):
            gr.Markdown("""
            ### 🌐 Scrape and Analyze Web Content
            Fetch content from any website, extract clean text, and analyze it.
            
            **⚠️ Limitations:**
            - Timeout: 30 seconds per request
            - Some sites block automated access (LinkedIn, Facebook, etc.)
            - JavaScript-heavy sites may not render fully
            - Rate limits apply to prevent abuse
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    web_input = gr.Textbox(
                        label="🔗 Website URL",
                        placeholder="https://example.com",
                        value="https://example.com",
                        info="Enter any public website URL"
                    )
                    web_btn = gr.Button(
                        "🌐 Fetch Website",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                    gr.Markdown("""
                    **💡 Tips:**
                    - Works with most public websites
                    - Extracts clean text (no HTML)
                    - Finds all page links
                    - Some sites block bots (e.g., LinkedIn)
                    """)
                
                with gr.Column(scale=2):
                    web_output = gr.Textbox(
                        label="📊 Website Content",
                        lines=20,
                        elem_classes=["output-class"]
                    )
            
            web_btn.click(tool_web_fetcher, inputs=[web_input], outputs=[web_output])
            
            gr.Examples([
                ["https://example.com"],
                ["https://python.org"],
                ["https://github.com"]
            ], inputs=[web_input], label="📚 Try These Examples")
        
        # ====== TAB 4: RAG SEARCH ======
        with gr.Tab("🔍 RAG Search"):
            gr.Markdown("""
            ### 🔍 Semantic Document Search with AI
            Search through documents using AI-powered semantic understanding (RAG - Retrieval Augmented Generation).
            
            **⚠️ Limitations:**
            - Currently searches 5 pre-loaded sample documents
            - First search: ~5-10 seconds (loads AI model)
            - Subsequent searches: ~1-2 seconds
            - Max 1000 documents supported
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    rag_input = gr.Textbox(
                        label="🔎 Search Query",
                        placeholder="What are you looking for?",
                        value="What is machine learning?",
                        lines=3,
                        info="Ask questions in natural language"
                    )
                    rag_btn = gr.Button(
                        "🔍 Search Documents",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                    gr.Markdown("""
                    **💡 How it works:**
                    - Uses AI embeddings (FAISS)
                    - Understands meaning, not just keywords
                    - Searches 5 sample documents
                    - Returns relevance scores
                    """)
                
                with gr.Column(scale=2):
                    rag_output = gr.Textbox(
                        label="📊 Search Results",
                        lines=20,
                        elem_classes=["output-class"]
                    )
            
            rag_btn.click(tool_rag_search, inputs=[rag_input], outputs=[rag_output])
            
            gr.Examples([
                ["What is machine learning?"],
                ["How to reduce carbon emissions?"],
                ["What are modern web frameworks?"],
                ["Digital marketing strategies"]
            ], inputs=[rag_input], label="📚 Try These Searches")
        
        # ====== TAB 5: DATA VISUALIZER ======
        with gr.Tab("📊 Data Visualizer"):
            gr.Markdown("""
            ### 📊 Create Beautiful Charts from Your Data
            Transform CSV data into stunning visualizations - line charts, bar charts, pie charts, and scatter plots.
            
            **⚠️ Limitations:**
            - Max 10,000 rows of data
            - CSV format only (comma-separated)
            - Generated as PNG images (800x600px)
            - Numeric columns required for pie/scatter charts
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    viz_csv = gr.Textbox(
                        label="📋 CSV Data",
                        lines=10,
                        value=load_sample_csv(),
                        placeholder="month,revenue,costs\nJan,100000,60000",
                        info="Paste your CSV data here"
                    )
                    viz_chart = gr.Radio(
                        ["line", "bar", "pie", "scatter"],
                        label="📈 Chart Type",
                        value="line",
                        info="Select visualization style"
                    )
                    viz_x = gr.Textbox(label="📍 X-Axis Column", value="month")
                    viz_y = gr.Textbox(label="📍 Y-Axis Column", value="revenue")
                    viz_title = gr.Textbox(label="📝 Chart Title", value="Monthly Revenue")
                    viz_btn = gr.Button(
                        "📊 Create Chart",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                
                with gr.Column(scale=2):
                    viz_output = gr.Textbox(
                        label="📊 Chart Status",
                        lines=5,
                        elem_classes=["output-class"]
                    )
                    viz_img = gr.Image(label="📈 Generated Chart", elem_classes=["chart-output"])
            
            viz_btn.click(
                tool_data_visualizer,
                inputs=[viz_csv, viz_chart, viz_x, viz_y, viz_title],
                outputs=[viz_output, viz_img]
            )
            
            gr.Markdown("*💡 Sample data is already loaded! Just click 'Create Chart' to see it in action.*")
        
        # ====== TAB 6: EMAIL CLASSIFIER ======
        with gr.Tab("📧 Email Classifier"):
            gr.Markdown("""
            ### 📧 AI-Powered Email Intent Detection
            Automatically classify email intent and detect sentiment - complaint, inquiry, urgent, etc.
            
            **⚠️ Limitations:**
            - Rule-based classification (not deep learning)
            - Max 10,000 characters per email
            - English language optimized
            - 10 intent categories supported
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    email_input = gr.Textbox(
                        label="✉️ Email Content",
                        lines=12,
                        value=load_sample_email(),
                        placeholder="Paste email content here...",
                        info="Paste any email text for analysis"
                    )
                    email_btn = gr.Button(
                        "🎯 Classify Email",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                    gr.Markdown("""
                    **💡 Detects 10 intents:**
                    - Complaint
                    - Inquiry
                    - Request
                    - Feedback
                    - Order
                    - Meeting
                    - Urgent
                    - Application
                    - Sales
                    - Other
                    """)
                
                with gr.Column(scale=2):
                    email_output = gr.Textbox(
                        label="📊 Classification Results",
                        lines=20,
                        elem_classes=["output-class"]
                    )
            
            email_btn.click(tool_email_classifier, inputs=[email_input], outputs=[email_output])
            
            gr.Examples([
                ["I am writing to complain about the poor service I received at your store yesterday."],
                ["Could you please send me more information about your pricing plans?"],
                ["URGENT: The server is down and customers cannot access the website!"]
            ], inputs=[email_input], label="📚 Try These Examples")
        
        # ====== TAB 7: KPI GENERATOR ======
        with gr.Tab("📈 KPI Generator"):
            gr.Markdown("""
            ### 📈 Business KPI & Analytics Dashboard
            Generate comprehensive business metrics and KPIs from your data automatically.
            
            **⚠️ Limitations:**
            - JSON format required
            - Max 50 KPIs calculated per request
            - Numeric data only for calculations
            - Processing time: ~1-2 seconds
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    kpi_json = gr.Textbox(
                        label="📊 Business Data (JSON Format)",
                        lines=14,
                        value=load_sample_json(),
                        placeholder='{"revenue": 1000000, "costs": 600000}',
                        info="Enter your business metrics in JSON"
                    )
                    kpi_metrics = gr.CheckboxGroup(
                        ["revenue", "growth", "efficiency", "customer", "operational"],
                        label="📋 Metrics to Calculate",
                        value=["revenue", "growth", "efficiency"],
                        info="Select which KPI categories to generate"
                    )
                    kpi_btn = gr.Button(
                        "📈 Generate KPIs",
                        variant="primary",
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                    gr.Markdown("""
                    **💡 Generates:**
                    - Revenue metrics
                    - Growth rates
                    - Efficiency ratios
                    - Customer metrics
                    - Operational KPIs
                    - Executive summary
                    """)
                
                with gr.Column(scale=2):
                    kpi_output = gr.Textbox(
                        label="📊 KPI Report",
                        lines=25,
                        elem_classes=["output-class"]
                    )
            
            kpi_btn.click(
                tool_kpi_generator,
                inputs=[kpi_json, kpi_metrics],
                outputs=[kpi_output]
            )
            
            gr.Markdown("*💡 Sample business data is already loaded! Just click 'Generate KPIs' to see results.*")
    
    # Footer
    gr.HTML("""
    <div class="footer">
        <h2 style="margin-bottom: 20px;">🎯 About MissionControlMCP</h2>
        
        <p style="font-size: 18px; margin-bottom: 20px;">
            <strong>8 enterprise-grade automation tools</strong> integrated with Claude Desktop via Model Context Protocol (MCP)
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 30px 0;">
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>📄 PDF Reader</strong><br/>
                <small>Extract text from documents</small>
            </div>
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>📝 Text Extractor</strong><br/>
                <small>Keywords & summaries</small>
            </div>
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>🌐 Web Fetcher</strong><br/>
                <small>Scrape websites</small>
            </div>
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>🔍 RAG Search</strong><br/>
                <small>Semantic search</small>
            </div>
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>📊 Data Visualizer</strong><br/>
                <small>Create charts</small>
            </div>
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>🔄 File Converter</strong><br/>
                <small>Format conversions</small>
            </div>
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>📧 Email Classifier</strong><br/>
                <small>Intent detection</small>
            </div>
            <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong>📈 KPI Generator</strong><br/>
                <small>Business analytics</small>
            </div>
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e9ecef;">
            <p style="font-size: 16px; margin: 10px 0;">
                🔗 <a href="https://github.com/AlBaraa-1/CleanEye-Hackathon" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">View on GitHub</a>
            </p>
            <p style="margin: 10px 0; color: #6c757d;">
                🏆 Built for HuggingFace Gradio x BuildWithMCP Hackathon
            </p>
            <p style="margin: 10px 0; color: #6c757d;">
                Made with ❤️ using Python, Gradio, Claude MCP, FAISS, and Sentence Transformers
            </p>
        </div>
    </div>
    """)


# ============================================================================
# LAUNCH
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Launching MissionControlMCP Web Interface...")
    print("="*80)
    
    # Launch with public sharing enabled
    demo.launch(
        share=True,  # Creates public URL!
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
