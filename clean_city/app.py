"""
CleanCity Agent - Main Gradio Application

A user-friendly web interface for trash detection and cleanup planning.
"""

import gradio as gr
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Optional, Tuple

from agents.planner_agent import run_cleanup_workflow, analyze_hotspots
from tools.history_tool import query_events
from llm_client import get_llm_client


# ============================================================================
# UI CONSTANTS & STYLES
# ============================================================================

TITLE = "🌍 CleanCity Agent"
TAGLINE = "Spot trash. Plan action. Keep your city clean."

GUIDE_CONTENT = """
## 📖 How to Use CleanCity Agent

### Step 1 – Add a Photo
Upload a picture of a street, beach, park, or any place where there might be trash. 
You can use your device's camera or select an existing image.

**Pro Tip:** Click the **📍 Get GPS** button to automatically capture your current location!

### Step 2 – Let the AI Spot the Trash
Click **"Start Analysis"**. Our AI will:
- Identify trash items in your image using your trained YOLO model
- Draw bounding boxes around detected objects
- Classify the type of trash found

### Step 3 – Review the Cleanup Plan
Get an instant assessment including:
- **Severity level** (Low/Medium/High)
- Number of volunteers needed
- Estimated cleanup time
- Required equipment list
- Environmental impact summary

### Step 4 – Save and Track
Save this event with a location to:
- Track trash patterns over time
- Identify recurring problem areas ("hotspots")
- Build evidence for city officials

### Step 5 – Share or Report
Use the generated report to:
- Contact your city's environmental department
- Organize community cleanup events
- Document progress for grants or awareness campaigns

---

### 💡 Tips
- **Better photos = better detection**: Take clear, well-lit images
- **Add location details**: Helps track hotspots and patterns
- **Check History tab**: See trends and recurring problem areas
- **Chat with the agent**: Ask questions about your analysis

### ⚠️ Limitations
This is an AI-powered prototype. Detection accuracy depends on image quality 
and lighting conditions. Always verify results visually.
"""

FAQ_CONTENT = """
## ❓ Frequently Asked Questions

**Q: How does the trash detection work?**  
A: We use computer vision models trained to recognize common litter items like 
plastic bottles, bags, food wrappers, cigarette butts, and more.

**Q: Is my data stored or shared?**  
A: All data is stored locally in your instance. We don't upload images or 
personal information to external servers (except LLM API calls if you configure them).

**Q: What should I do if detection is inaccurate?**  
A: The mock model provides random detections for demonstration. Replace with a 
real model by updating `trash_model.py`. You can also add notes to manually 
correct assessments.

**Q: Can I use this for large-scale city monitoring?**  
A: This is a prototype designed for community groups and individual activists. 
For large-scale deployment, consider:
- Integrating a production-grade detection model
- Setting up cloud hosting for data persistence
- Adding user authentication and role management

**Q: How can I contribute or report issues?**  
A: Check the project repository for contribution guidelines and issue tracking.
"""


# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================

def draw_boxes_on_image(image: Image.Image, detections: list) -> Image.Image:
    """Draw bounding boxes and labels on image."""
    if not detections:
        return image
    
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    
    # Try to load a font, fall back to default if unavailable
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    for det in detections:
        bbox = det["bbox"]
        label = det["label"].replace("_", " ").title()
        score = det["score"]
        
        # Draw rectangle
        draw.rectangle(bbox, outline="red", width=3)
        
        # Draw label background
        text = f"{label} ({score:.0%})"
        
        # Get text bounding box for background
        try:
            text_bbox = draw.textbbox((bbox[0], bbox[1] - 20), text, font=font)
            draw.rectangle(text_bbox, fill="red")
            draw.text((bbox[0], bbox[1] - 20), text, fill="white", font=font)
        except:
            # Fallback for older Pillow versions
            draw.text((bbox[0], bbox[1] - 20), text, fill="red", font=font)
    
    return img_copy


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# ============================================================================
# CORE ANALYSIS FUNCTION
# ============================================================================

def analyze_image(
    image: Optional[Image.Image],
    location: str,
    notes: str,
    save_to_history: bool,
    gps_coords: str
) -> Tuple[Optional[Image.Image], str, str, str]:
    """
    Main analysis function called when user clicks "Start Analysis".
    
    Returns:
        - annotated_image: Image with bounding boxes
        - detection_text: Detection results summary
        - plan_text: Cleanup plan
        - report_text: Generated report
    """
    if image is None:
        return None, "⚠️ Please upload an image first.", "", ""
    
    # Parse GPS coordinates if provided
    latitude, longitude = None, None
    if gps_coords and gps_coords.strip():
        try:
            parts = gps_coords.split(',')
            if len(parts) == 2:
                latitude = float(parts[0].strip())
                longitude = float(parts[1].strip())
        except:
            pass  # Invalid format, continue without coords
    
    try:
        # Run the full workflow
        result = run_cleanup_workflow(
            image=image,
            location=location if location.strip() else None,
            notes=notes if notes.strip() else None,
            save_to_history=save_to_history,
            use_llm_enhancement=False,  # Can make this a checkbox
            latitude=latitude,
            longitude=longitude
        )
        
        if result["status"] == "no_trash":
            return image, result["summary"], "", ""
        
        # Draw boxes on image
        annotated_image = draw_boxes_on_image(
            image,
            result["detection_results"]["detections"]
        )
        
        # Format detection results
        detection_text = f"""### 🔍 Detection Results

{result['detection_results']['summary']}

**Items Detected:**
"""
        for det in result["detection_results"]["detections"]:
            label = det["label"].replace("_", " ").title()
            detection_text += f"- {label} (confidence: {det['score']:.0%})\n"
        
        # Format plan
        plan = result["plan"]
        plan_text = f"""### 📋 Cleanup Plan

**Severity Level:** {plan['severity'].upper()}

**Resources Needed:**
- 👥 Volunteers: {plan['recommended_volunteers']}
- ⏱️ Estimated Time: {plan['estimated_time_minutes']} minutes
- 📅 Urgency: Within {plan['urgency_days']} day(s)

**Equipment:**
"""
        for item in plan['equipment_needed']:
            plan_text += f"- {item}\n"
        
        plan_text += f"\n**Environmental Impact:**\n{plan['environmental_impact']}\n"
        
        if result.get("event_id"):
            plan_text += f"\n✅ Saved! ID: {result['event_id']}"
        
        # Return report
        report_text = result["report"]
        
        return annotated_image, detection_text, plan_text, report_text
    
    except Exception as e:
        error_msg = f"❌ Error during analysis: {str(e)}"
        return image, error_msg, "", ""


# ============================================================================
# HISTORY & HOTSPOT FUNCTIONS
# ============================================================================

def load_history(days_filter: int, location_filter: str, severity_filter: str) -> str:
    """Load and format event history."""
    try:
        # Apply filters
        query_params = {"days": days_filter if days_filter > 0 else None}
        
        if location_filter.strip():
            query_params["location"] = location_filter.strip()
        
        if severity_filter != "All":
            query_params["severity"] = severity_filter.lower()
        
        result = query_events(**query_params)
        
        if not result["events"]:
            return "No events found matching your filters."
        
        # Format output
        output = f"""### 📊 Event History

**Summary:**
- Total events: {result['summary']['total_events']}
- Total trash items: {result['summary']['total_trash_items']}
- Average per event: {result['summary']['avg_trash_per_event']:.1f}
- Unique locations: {result['summary']['unique_locations']}

---

**Recent Events:**

"""
        for event in result["events"][:20]:  # Show last 20
            output += f"""
**Event #{event['id']}** - {event['timestamp'][:19]}
- Location: {event['location'] or 'Not specified'}
- Severity: {event['severity'].upper()}
- Items: {event['trash_count']}
- Categories: {', '.join(event['categories'])}
- Status: {'✅ Cleaned' if event['cleaned'] else '⏳ Pending'}
---
"""
        
        return output
    
    except Exception as e:
        return f"❌ Error loading history: {str(e)}"


def load_hotspots(days: int) -> str:
    """Load and format hotspot analysis."""
    try:
        result = analyze_hotspots(days=days)
        
        if not result["hotspots"]:
            return result.get("message", "No hotspots found.")
        
        output = f"""### 🔥 Trash Hotspots Analysis

{result['recommendation']}

---

**All Hotspots ({result['count']} locations):**

"""
        for i, hotspot in enumerate(result["hotspots"], 1):
            output += f"""
**{i}. {hotspot['location']}**
- Events: {hotspot['event_count']}
- Total trash items: {hotspot['total_trash']}
- Average per event: {hotspot['avg_trash']:.1f}
- Last seen: {hotspot['last_event'][:19]}
- Severity levels: {hotspot['severities']}
---
"""
        
        return output
    
    except Exception as e:
        return f"❌ Error analyzing hotspots: {str(e)}"


# ============================================================================
# CHATBOT FUNCTION
# ============================================================================

def chat_with_agent(message: str, history: list) -> str:
    """Handle chat interactions with the CleanCity agent."""
    try:
        llm = get_llm_client()
        
        # Build context from history
        context = ""
        for user_msg, bot_msg in history:
            context += f"User: {user_msg}\nAgent: {bot_msg}\n"
        
        # System prompt
        system_prompt = """You are CleanCity Agent, a helpful AI assistant focused on 
environmental cleanup and trash management. You help users:
- Understand their trash detection results
- Plan effective cleanup operations
- Organize community action
- Report issues to authorities
- Analyze environmental impact

Be friendly, practical, and encouraging. Keep responses concise but informative."""
        
        prompt = f"{context}User: {message}\nAgent:"
        
        response = llm.generate_text(
            prompt,
            system_prompt=system_prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        return response
    
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try again or check your LLM configuration."


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_interface() -> gr.Blocks:
    """Create and configure the Gradio interface."""
    
    with gr.Blocks(
        title="CleanCity Agent",
        theme=gr.themes.Soft(primary_hue="green")
    ) as app:
        # Header
        gr.Markdown(f"# {TITLE}")
        gr.Markdown(f"*{TAGLINE}*")
        
        with gr.Tabs():
            # ================================================================
            # TAB 1: MAIN ANALYSIS
            # ================================================================
            with gr.Tab("🔍 Analyze Image"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Upload Image")
                        image_input = gr.Image(
                            type="pil",
                            label="Street/Beach/Park Image",
                            sources=["upload", "webcam"]
                        )
                        
                        with gr.Row():
                            location_input = gr.Textbox(
                                label="Location (optional)",
                                placeholder="e.g., Main Street Park, Downtown Beach...",
                                lines=1,
                                scale=4
                            )
                            get_location_btn = gr.Button(
                                "📍 Get GPS",
                                size="sm",
                                scale=1
                            )
                        
                        gps_coords = gr.Textbox(
                            label="GPS Coordinates",
                            placeholder="Latitude, Longitude (auto-filled when you click Get GPS)",
                            lines=1,
                            interactive=False,
                            visible=False
                        )
                        
                        notes_input = gr.Textbox(
                            label="Notes (optional)",
                            placeholder="Any additional context...",
                            lines=2
                        )
                        
                        save_history = gr.Checkbox(
                            label="Save to history",
                            value=True
                        )
                        
                        analyze_btn = gr.Button(
                            "🚀 Start Analysis",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Detection Results")
                        output_image = gr.Image(
                            type="pil",
                            label="Annotated Image"
                        )
                
                gr.Markdown("---")
                
                with gr.Row():
                    with gr.Column():
                        detection_output = gr.Markdown(label="Detections")
                    
                    with gr.Column():
                        plan_output = gr.Markdown(label="Cleanup Plan")
                
                gr.Markdown("### 📄 Generated Report")
                report_output = gr.Textbox(
                    label="Email Report (copy & send to authorities)",
                    lines=15,
                    max_lines=20
                )
                
                # Wire up the analyze button
                analyze_btn.click(
                    fn=analyze_image,
                    inputs=[image_input, location_input, notes_input, save_history, gps_coords],
                    outputs=[output_image, detection_output, plan_output, report_output]
                )
                
                # Wire up GPS button with JavaScript to get browser location
                get_location_btn.click(
                    fn=None,
                    inputs=[],
                    outputs=[location_input, gps_coords],
                    js="""
                    async () => {
                        try {
                            const position = await new Promise((resolve, reject) => {
                                navigator.geolocation.getCurrentPosition(resolve, reject, {
                                    enableHighAccuracy: true,
                                    timeout: 10000
                                });
                            });
                            
                            const lat = position.coords.latitude.toFixed(6);
                            const lon = position.coords.longitude.toFixed(6);
                            const coords = lat + ', ' + lon;
                            
                            // Reverse geocode to get location name
                            try {
                                const response = await fetch(
                                    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`
                                );
                                const data = await response.json();
                                const location = data.display_name || `Location at ${coords}`;
                                return [location, coords];
                            } catch (e) {
                                return [`Location at ${coords}`, coords];
                            }
                        } catch (error) {
                            alert('GPS Error: ' + error.message + '\\n\\nPlease enable location services in your browser.');
                            return ['', ''];
                        }
                    }
                    """
                )
            
            # ================================================================
            # TAB 2: USER GUIDE
            # ================================================================
            with gr.Tab("📖 How It Works"):
                gr.Markdown(GUIDE_CONTENT)
                gr.Markdown("---")
                gr.Markdown(FAQ_CONTENT)
            
            # ================================================================
            # TAB 3: HISTORY
            # ================================================================
            with gr.Tab("📊 Event History"):
                gr.Markdown("### View Past Trash Detection Events")
                
                with gr.Row():
                    days_filter = gr.Slider(
                        minimum=0,
                        maximum=365,
                        value=30,
                        step=1,
                        label="Last N days (0 = all time)"
                    )
                    location_filter = gr.Textbox(
                        label="Filter by location (partial match)",
                        placeholder="e.g., Park"
                    )
                    severity_filter = gr.Dropdown(
                        choices=["All", "Low", "Medium", "High"],
                        value="All",
                        label="Filter by severity"
                    )
                
                load_history_btn = gr.Button("🔄 Load History", variant="primary")
                history_output = gr.Markdown()
                
                load_history_btn.click(
                    fn=load_history,
                    inputs=[days_filter, location_filter, severity_filter],
                    outputs=history_output
                )
            
            # ================================================================
            # TAB 4: HOTSPOTS
            # ================================================================
            with gr.Tab("🔥 Hotspot Analysis"):
                gr.Markdown("### Identify Recurring Problem Areas")
                gr.Markdown(
                    "Hotspots are locations with multiple trash events. "
                    "Use this to prioritize cleanup efforts and request permanent solutions."
                )
                
                hotspot_days = gr.Slider(
                    minimum=7,
                    maximum=365,
                    value=30,
                    step=7,
                    label="Analyze last N days"
                )
                
                load_hotspots_btn = gr.Button("🔍 Find Hotspots", variant="primary")
                hotspots_output = gr.Markdown()
                
                load_hotspots_btn.click(
                    fn=load_hotspots,
                    inputs=hotspot_days,
                    outputs=hotspots_output
                )
            
            # ================================================================
            # TAB 5: CHAT WITH AGENT
            # ================================================================
            with gr.Tab("💬 Chat with Agent"):
                gr.Markdown("### Ask Questions or Get Help")
                gr.Markdown(
                    "Chat with the CleanCity Agent to get advice on cleanup strategies, "
                    "interpretation of results, or general environmental questions."
                )
                
                chatbot = gr.Chatbot(height=500)
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Ask me anything about cleanup planning..."
                )
                
                with gr.Row():
                    submit = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear Chat")
                
                def respond(message, chat_history):
                    bot_response = chat_with_agent(message, chat_history)
                    chat_history.append((message, bot_response))
                    return "", chat_history
                
                submit.click(respond, [msg, chatbot], [msg, chatbot])
                msg.submit(respond, [msg, chatbot], [msg, chatbot])
                clear.click(lambda: [], None, chatbot)
        
        # Footer
        gr.Markdown("---")
        gr.Markdown(
            "*CleanCity Agent is a prototype tool for community environmental action. "
            "Always verify AI results manually before taking action.*"
        )
    
    return app


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

# Create the Gradio app at module level for HuggingFace Spaces compatibility
print("=" * 60)
print("🌍 CleanCity Agent - Initializing...")
print("=" * 60)

# Initialize LLM client (will print status)
get_llm_client()

print("\n✓ Creating Gradio interface...")
app = create_interface()
print("✓ Gradio interface ready!")
print("=" * 60 + "\n")


def main():
    """Launch the Gradio application (local development)."""
    print("🚀 Launching web server...")
    print("Access the app at: http://localhost:7860\n")
    
    app.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,
        share=False,  # Set to True to create public link
        show_error=True
    )


if __name__ == "__main__":
    main()
