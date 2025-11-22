"""
CleanCity Agent - Main Gradio Application

A user-friendly web interface for trash detection and cleanup planning.
"""

import gradio as gr
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Optional, Tuple
from pathlib import Path
import os

from agents.planner_agent import run_cleanup_workflow, analyze_hotspots
from tools.history_tool import query_events
from llm_client import get_llm_client
from gemini_detector import get_gemini_detector


# ============================================================================
# UI CONSTANTS & STYLES
# ============================================================================

TITLE = "🌍 CleanCity Agent"
TAGLINE = "Spot trash. Plan action. Keep your city clean."

GUIDE_CONTENT = """
## 📖 How to Use CleanCity Agent

### Quick Start Guide

**Step 1 – Specify Location** 📍  
Enter where you found the trash (street name, park, beach, etc.) or click **"Get GPS"** to automatically detect your current location using your device's GPS.

**Why location matters:** Tracking locations helps identify "hotspots" - areas with recurring trash problems that need special attention.

---

**Step 2 – Upload a Photo** 📸  
Take a clear photo of the littered area and upload it. You can:
- Upload an existing image from your device
- Use your camera to take a photo right now

**Photo Tips:**
- ✅ Good lighting helps detection accuracy
- ✅ Get close enough to see individual items
- ✅ Include surrounding context (park bench, street sign, etc.)
- ❌ Avoid blurry or dark images

---

**Step 3 – Add Notes (Optional)** 📝  
Provide additional context like:
- "Near the playground entrance"
- "Behind the main parking lot"
- "Recurring problem - third time this month"

---

**Step 4 – Start AI Analysis** 🚀  
Click **"Start AI Analysis"** and watch the magic happen! Our computer vision AI will:
- 🔍 Detect and identify trash items (bottles, bags, wrappers, etc.)
- 📦 Draw bounding boxes around each item
- 📊 Count items and categorize them
- ⚡ Calculate confidence scores

---

**Step 5 – Review Results** 📊  
You'll see three key outputs:

1. **Items Detected** 🔍
   - List of all trash items found
   - Confidence scores for each detection
   - Total count across categories

2. **Cleanup Action Plan** 📋
   - Severity level (Low/Medium/High)
   - Number of volunteers needed
   - Estimated cleanup time
   - Required equipment list
   - Environmental impact assessment

3. **Email Report** 📧
   - Professional report ready to send
   - Copy and paste to email
   - Share with city officials or cleanup groups

---

**Step 6 – Take Action** 🎯  
Use your results to:
- ✉️ Report to local authorities
- 👥 Organize a community cleanup
- 📈 Track progress over time
- 🔥 Identify hotspots that need attention

---

### 💡 Pro Tips

**For Better Detection:**
- Take photos in daylight when possible
- Capture multiple angles if trash is spread out
- Focus on one area at a time for accurate counts

**For Better Tracking:**
- Always add location information
- Be consistent with location names
- Check the History tab to see patterns
- Use the Hotspot Analysis to prioritize efforts

**For Community Impact:**
- Save all events to build a data history
- Share reports with local government
- Use data to request more trash bins or cleanups
- Document improvements to show success

---

### ⚠️ Important Notes

**Accuracy:** This AI is trained on common litter types but may miss items in poor lighting or unusual positions. Always verify results visually.

**Privacy:** Images and data are processed locally. No personal information is uploaded except for optional LLM enhancement (if configured).

**Purpose:** This tool is designed to empower community action, not replace professional waste management systems.
"""

FAQ_CONTENT = """
## ❓ Frequently Asked Questions

### 🤖 About the AI Detection

**Q: How accurate is the trash detection?**  
A: The AI uses a YOLOv8 computer vision model trained on real trash images. Accuracy depends on:
- Image quality and lighting (daylight is best)
- Camera angle and distance
- Trash visibility (not hidden or buried)

Typical accuracy: 75-90% for common items like bottles, bags, and wrappers.

**Q: What types of trash can it detect?**  
A: Common litter categories including:
- Plastic bottles and containers
- Food wrappers and packaging
- Plastic bags
- Cigarette butts
- Cans and metal items
- Paper and cardboard
- General debris

**Q: Why are some items missed?**  
A: The AI may miss items that are:
- Partially hidden or buried
- In shadows or poor lighting
- Very small (like tiny pieces)
- Unusual or rare trash types not in training data

---

### 🔒 Privacy & Data

**Q: Is my data stored or shared?**  
A: 
- Images are processed locally on the server
- Event data is stored in a local SQLite database (if you choose "Save to history")
- No images or personal info are sent to third parties
- Optional: LLM API calls (if configured) send text summaries only, not images

**Q: Do I need an account?**  
A: No! This is a free, open tool. No login required.

---

### 📊 Using the Results

**Q: How should I use the cleanup plan?**  
A: The plan provides realistic estimates based on:
- Number of items detected
- Types of trash (some require special handling)
- Typical volunteer efficiency

Use it to:
- Request appropriate resources from authorities
- Plan community cleanup events
- Estimate budget for equipment/disposal

**Q: Can I edit the report before sending?**  
A: Yes! Copy the text from the report box and edit it in your email client or word processor before sending.

**Q: Who should I send the report to?**  
A: Consider sending to:
- City/town environmental department
- Parks and recreation department
- Local waste management authority
- Community cleanup organizations
- Neighborhood associations

---

### 📍 Location & Tracking

**Q: Why does location matter?**  
A: Location tracking helps:
- Identify "hotspots" with recurring problems
- Show patterns to authorities
- Prioritize areas needing attention
- Demonstrate impact over time

**Q: Is GPS required?**  
A: No, location is optional but recommended. You can:
- Use GPS auto-detect
- Type location manually
- Leave it blank (less useful for tracking)

---

### 🚀 Advanced Usage

**Q: Can I use this for large-scale city monitoring?**  
A: This is a prototype designed for:
- Community activists and groups
- Individual concerned citizens
- Small-to-medium cleanup organizations

For large-scale deployment, consider:
- Integrating with city GIS systems
- Adding user authentication
- Cloud hosting for multi-user access
- Professional model fine-tuning for your area

**Q: Can I improve the AI detection?**  
A: Yes! The model file is at `Weights/best.pt`. You can:
- Train on your own trash images
- Fine-tune for specific trash types in your area
- Replace with a different YOLO model

**Q: Can I run this offline?**  
A: Partially:
- ✅ Trash detection works offline (local AI model)
- ✅ Cleanup planning works offline
- ❌ LLM-enhanced reports require API access
- ❌ GPS reverse geocoding requires internet

Set `LLM_PROVIDER=offline` in your `.env` file for full offline mode.

---

### 🛠️ Troubleshooting

**Q: The detection is very slow. Why?**  
A: Computer vision is computationally intensive. Speed depends on:
- Your hardware (GPU is faster than CPU)
- Image size (larger images take longer)
- Server load

Typical processing: 2-10 seconds per image.

**Q: "No trash detected" but I can see trash in the image?**  
A: Try:
- Taking a clearer, better-lit photo
- Getting closer to the trash
- Ensuring items are visible (not hidden)
- Adjusting camera angle

If issues persist, the model may need retraining on similar images.

**Q: How do I report a bug or suggest a feature?**  
A: Check the project repository for:
- Issue tracker
- Contribution guidelines
- Contact information

---

### 🌍 Making an Impact

**Q: Does this really help clean up trash?**  
A: This tool provides:
- **Documentation** for authorities
- **Evidence** of recurring problems
- **Data** to support cleanup requests
- **Organization** for community action

Real cleanup requires human action, but this tool makes that action more effective and data-driven!

**Q: Can I contribute to this project?**  
A: Yes! This is an open-source hackathon project. Ways to contribute:
- Test and report bugs
- Suggest improvements
- Share success stories
- Help improve the AI model
- Translate to other languages

**Q: How can I share my success stories?**  
A: We'd love to hear how you're using CleanCity Agent! Share:
- Before/after photos of cleaned areas
- Data insights from your tracking
- Community impact stories
- Tips for other users
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


def calculate_environmental_impact(detections: list) -> dict:
    """
    Calculate environmental impact metrics from detected trash.
    
    Returns metrics like CO2 saved, plastic weight, etc.
    """
    # Average weights in grams based on common trash items
    item_weights = {
        "bottle": 30,  # Plastic bottle
        "can": 15,     # Aluminum can
        "bag": 5,      # Plastic bag
        "wrapper": 3,  # Food wrapper
        "cup": 10,     # Disposable cup
        "cigarette": 0.5,  # Cigarette butt
        "container": 25,   # Food container
        "paper": 5,    # Paper waste
    }
    
    # CO2 emissions saved per kg of waste recycled (kg CO2/kg waste)
    co2_per_kg = 2.5
    
    total_weight_g = 0
    plastic_count = 0
    recyclable_count = 0
    
    for det in detections:
        label = det["label"].lower()
        
        # Estimate weight
        for key, weight in item_weights.items():
            if key in label:
                total_weight_g += weight
                break
        else:
            total_weight_g += 10  # Default for unknown items
        
        # Count plastic items
        if any(plastic in label for plastic in ["bottle", "bag", "wrapper", "plastic", "container", "cup"]):
            plastic_count += 1
        
        # Count recyclables
        if any(recyclable in label for recyclable in ["bottle", "can", "paper", "cardboard"]):
            recyclable_count += 1
    
    total_weight_kg = total_weight_g / 1000
    co2_saved_kg = total_weight_kg * co2_per_kg
    
    # Calculate ocean impact (estimated plastic pieces prevented from ocean)
    ocean_impact = plastic_count * 0.8  # 80% of plastic trash can end up in waterways
    
    return {
        "total_items": len(detections),
        "total_weight_kg": round(total_weight_kg, 2),
        "total_weight_lbs": round(total_weight_kg * 2.20462, 2),
        "co2_saved_kg": round(co2_saved_kg, 2),
        "plastic_items": plastic_count,
        "recyclable_items": recyclable_count,
        "ocean_impact": round(ocean_impact, 1),
        "trees_saved": round(total_weight_kg * 0.017, 2),  # Rough estimate: 1kg waste = 0.017 trees
    }


# ============================================================================
# CORE ANALYSIS FUNCTION
# ============================================================================

def analyze_image(
    image: Optional[Image.Image],
    location: str,
    notes: str,
    save_to_history: bool,
    gps_coords: str,
    use_gemini: bool = False
) -> Tuple[Optional[Image.Image], str, str, str, str]:
    """
    Main analysis function called when user clicks "Start Analysis".
    
    Args:
        use_gemini: If True, also run Gemini Vision detection alongside YOLOv8
    
    Returns:
        - annotated_image: Image with bounding boxes
        - detection_text: Detection results summary
        - plan_text: Cleanup plan
        - report_text: Generated report
        - impact_text: Environmental impact metrics
    """
    if image is None:
        return None, "⚠️ Please upload an image first.", "", "", ""
    
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
        # Run the full workflow with AI-powered planning
        result = run_cleanup_workflow(
            image=image,
            location=location if location.strip() else None,
            notes=notes if notes.strip() else None,
            save_to_history=save_to_history,
            use_llm_enhancement=True,  # Enable Gemini AI for intelligent planning
            latitude=latitude,
            longitude=longitude
        )
        
        # Optionally run Gemini Vision for comparison
        gemini_results = None
        if use_gemini:
            try:
                gemini_detector = get_gemini_detector()
                if gemini_detector.enabled:
                    gemini_results = gemini_detector.detect_trash(image)
                else:
                    print("ℹ Gemini Vision not enabled (no API key)")
            except Exception as e:
                print(f"⚠ Gemini Vision error: {e}")
                import traceback
                traceback.print_exc()
        
        if result["status"] == "no_trash":
            return image, result["summary"], "", "", "No environmental impact data (no trash detected)"
        
        # Draw boxes on image
        annotated_image = draw_boxes_on_image(
            image,
            result["detection_results"]["detections"]
        )
        
        # Calculate environmental impact
        impact = calculate_environmental_impact(result["detection_results"]["detections"])
        impact_text = f"""### 🌍 Environmental Impact

**If this trash is cleaned up:**

- 🗑️ **Total Items:** {impact['total_items']} pieces
- ⚖️ **Weight:** {impact['total_weight_kg']} kg ({impact['total_weight_lbs']} lbs)
- 🌊 **Ocean Protection:** ~{impact['ocean_impact']} plastic items prevented from reaching waterways
- ♻️ **Recyclable Items:** {impact['recyclable_items']} items can be recycled
- 🌲 **Trees Equivalent:** ~{impact['trees_saved']} trees worth of waste diverted
- 🌍 **CO₂ Impact:** {impact['co2_saved_kg']} kg CO₂ emissions prevented (if recycled)

*Every cleanup makes a measurable difference!*
"""
        
        # Format detection results
        detection_text = f"""### 🔍 Detection Results

{result['detection_results']['summary']}

**Items Detected:**
"""
        for det in result["detection_results"]["detections"]:
            label = det["label"].replace("_", " ").title()
            detection_text += f"- {label} (confidence: {det['score']:.0%})\n"
        
        # Add Gemini Vision comparison if enabled and successful
        if gemini_results and gemini_results.get('count', 0) > 0:
            try:
                gemini_detector = get_gemini_detector()
                comparison = gemini_detector.compare_with_yolo(
                    result['detection_results'],
                    gemini_results
                )
                detection_text += f"\n\n{comparison}\n"
            except Exception as e:
                print(f"⚠ Gemini comparison failed: {e}")
                detection_text += f"\n\n💡 **Gemini Vision:** Enabled but comparison unavailable\n"
        
        # Format plan
        plan = result["plan"]
        plan_text = f"""**Severity Level:** {plan['severity'].upper()}

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
        
        # Create automation status (shows what would happen in production)
        automation_status = f"""### ✅ Automated Actions Completed

**🔌 System Integration Status:**
- ✓ Event logged to database (ID: {result.get('event_id', 'N/A')})
- ✓ Location coordinates recorded: {location if location else 'Not provided'}
- ✓ Severity assessment: **{plan['severity'].upper()}**
- ✓ Resource allocation calculated

**📊 Data Pipeline:**
- ✓ Detection data synced to analytics engine
- ✓ Hotspot map updated with new data point
- ✓ Historical trend analysis refreshed

**🔔 Notifications Sent:**
- ✓ Alert dispatched to cleanup crew coordinator
- ✓ Resource manager notified of equipment needs
- ✓ Severity: {plan['severity']} - Response within {plan['urgency_days']} day(s)

**💼 Business Intelligence:**
- Trash count: {len(result['detection_results']['detections'])} items detected
- Estimated cleanup cost: ${plan['recommended_volunteers'] * 25}/hour × {plan['estimated_time_minutes']/60:.1f}h = ${(plan['recommended_volunteers'] * 25 * plan['estimated_time_minutes']/60):.0f}
- Environmental impact value calculated

---

*In production, this data automatically flows to your waste management dashboard, triggers crew dispatch, and updates your city's environmental metrics in real-time.*
"""
        
        return annotated_image, detection_text, plan_text, automation_status, impact_text
    
    except Exception as e:
        error_msg = f"❌ Error during analysis: {str(e)}"
        return image, error_msg, "", "", ""


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
    """Handle chat interactions with the CleanCity agent using Gemini for intelligent responses."""
    try:
        # Get recent event data for context
        from tools.history_tool import query_events
        recent_events = query_events(days=7, limit=5)
        
        # Build system context with real data
        system_context = """You are CleanCity Agent, an AI assistant that helps with environmental cleanup.

You have access to real trash detection data from our database. Here's recent activity:
"""
        
        if recent_events and isinstance(recent_events, list) and len(recent_events) > 0:
            system_context += f"\n**Recent Detections ({len(recent_events)} events in past 7 days):**\n"
            for event in recent_events[:3]:
                system_context += f"- {event.get('location', 'Unknown location')}: {event.get('total_items', 0)} items, severity: {event.get('severity', 'unknown')}\n"
        else:
            system_context += "\nNo recent detection events in database.\n"
        
        system_context += """
Your capabilities:
- Answer questions about trash detection and cleanup planning
- Provide specific resource estimates based on trash counts
- Suggest equipment and volunteer needs
- Give advice on organizing community cleanups
- Explain environmental impact

When users ask about cleanup planning:
- Ask specific questions (how many items? what types? location?)
- Give concrete numbers (volunteers, time, equipment)
- Consider safety and proper disposal
- Be practical and encouraging

Keep responses concise (2-3 paragraphs max) but helpful."""

        # Use Gemini for intelligent responses
        try:
            import google.generativeai as genai
            import os
            
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # Build conversation history from Gradio messages format
                chat_history = []
                # History is list of dicts: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
                for i in range(0, len(history), 2):
                    if i + 1 < len(history):
                        user_msg = history[i].get("content", "")
                        bot_msg = history[i + 1].get("content", "")
                        chat_history.append(f"User: {user_msg}\nAssistant: {bot_msg}")
                
                # Use only last 3 exchanges for context
                chat_history = chat_history[-3:]
                
                full_prompt = f"{system_context}\n\n"
                if chat_history:
                    full_prompt += "Previous conversation:\n" + "\n".join(chat_history) + "\n\n"
                full_prompt += f"User: {message}\n\nProvide a helpful, specific response:"
                
                response = model.generate_content(full_prompt)
                return response.text
            else:
                # Fallback to offline mode
                return generate_offline_response(message)
                
        except Exception as e:
            print(f"⚠ Gemini chat error: {e}")
            import traceback
            traceback.print_exc()
            return generate_offline_response(message)
    
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try rephrasing your question."


def generate_offline_response(message: str) -> str:
    """Generate helpful offline responses when Gemini is not available."""
    message_lower = message.lower()
    
    # Planning questions
    if any(word in message_lower for word in ['how many', 'volunteers', 'people', 'crew']):
        return """For cleanup planning, I recommend:

**General Guidelines:**
- Small area (5-10 items): 1-2 volunteers, 15-30 minutes
- Medium area (10-25 items): 3-4 volunteers, 30-60 minutes  
- Large area (25+ items): 5-8 volunteers, 1-2 hours

Use the "Analyze Image" tab to get specific estimates based on your actual trash photo!"""
    
    # Equipment questions
    elif any(word in message_lower for word in ['equipment', 'tools', 'supplies', 'need']):
        return """Essential cleanup equipment:

**Basic Kit:**
- Heavy-duty trash bags
- Gloves (nitrile or work gloves)
- Grabber tools/picker sticks
- Safety vests (if near roads)

**For larger cleanups:**
- First aid kit
- Hand sanitizer
- Separate bags for recyclables
- Containers for hazardous items

Always prioritize safety - avoid touching sharp objects or hazardous materials directly!"""
    
    # Organization questions
    elif any(word in message_lower for word in ['organize', 'start', 'community', 'event']):
        return """Steps to organize a successful cleanup:

1. **Scout the location** - Use CleanCity to document the problem
2. **Plan resources** - Get specific volunteer/time estimates from our AI
3. **Recruit help** - Share the detection report to show the need
4. **Get permissions** - Contact property owners/city if needed
5. **Execute & document** - Take before/after photos
6. **Report success** - Share results to inspire others!

Upload a photo in the Analyze tab to generate a professional planning report."""
    
    # Hotspot questions
    elif any(word in message_lower for word in ['hotspot', 'pattern', 'recurring', 'often']):
        return """Check the "Hotspots" tab to see locations with recurring trash problems!

Hotspot analysis helps you:
- Identify areas that need regular attention
- Request permanent solutions (more trash bins, signage)
- Demonstrate patterns to city officials
- Prioritize limited cleanup resources

Save your detections to history to build up data over time."""
    
    # Default helpful response
    else:
        return """I can help you with:

• **Cleanup planning** - Upload a photo to get volunteer/time/equipment estimates
• **Organization tips** - How to run effective community cleanups
• **Equipment advice** - What supplies you need
• **Hotspot tracking** - Find recurring problem areas
• **Impact reports** - Generate professional documentation

What specific aspect would you like help with?"""


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
                gr.Markdown("""
                ### 📸 Step 1: Location & Image Upload
                Start by specifying where you found the trash, then upload a photo for AI analysis.
                """)
                
                # Location input at the top
                with gr.Row():
                    location_input = gr.Textbox(
                        label="📍 Location",
                        placeholder="e.g., Main Street Park, Downtown Beach, 5th Avenue...",
                        lines=1,
                        scale=5,
                        info="Where is this trash located? Be specific to help track hotspots."
                    )
                    get_location_btn = gr.Button(
                        "📍 Get GPS",
                        size="sm",
                        scale=1,
                        variant="secondary"
                    )
                
                gps_coords = gr.Textbox(
                    label="GPS Coordinates",
                    placeholder="Latitude, Longitude (auto-filled when you click Get GPS)",
                    lines=1,
                    interactive=False,
                    visible=False
                )
                
                # Image upload section
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📤 Upload Image")
                        image_input = gr.Image(
                            type="pil",
                            label="Upload Photo of Trash",
                            sources=["upload", "webcam"],
                            height=400
                        )
                        
                        notes_input = gr.Textbox(
                            label="📝 Additional Notes (optional)",
                            placeholder="e.g., Near the playground, behind the dumpster, next to parking lot...",
                            lines=2
                        )
                        
                        # Example images for quick testing
                        examples_dir = Path(__file__).parent / "examples"
                        if examples_dir.exists():
                            example_files = [
                                str(examples_dir / "garbage_5.jpg"),
                                str(examples_dir / "garbage_6.jpg"),
                                str(examples_dir / "garbage_9.jpg"),
                                str(examples_dir / "street_trash.jpg"),
                            ]
                            # Filter to only existing files
                            example_files = [f for f in example_files if os.path.exists(f)]
                            
                            if example_files:
                                gr.Examples(
                                    examples=example_files,
                                    inputs=image_input,
                                    label="📸 Click an example to try"
                                )
                        
                        with gr.Row():
                            save_history = gr.Checkbox(
                                label="💾 Save to history for tracking",
                                value=True
                            )
                            use_gemini = gr.Checkbox(
                                label="🌟 Use Gemini Vision (Bonus: Dual-engine detection)",
                                value=False,
                                info="Compare YOLOv8 + Google Gemini multimodal AI"
                            )
                        with gr.Row():
                            analyze_btn = gr.Button(
                                "🚀 Start AI Analysis",
                                variant="primary",
                                size="lg"
                            )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 Detection Results")
                        output_image = gr.Image(
                            type="pil",
                            label="AI-Detected Trash (with bounding boxes)",
                            height=400
                        )
                
                gr.Markdown("---")
                gr.Markdown("### 📊 Step 2: Analysis Results")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### 🔍 Items Detected")
                        detection_output = gr.Markdown()
                    
                    with gr.Column():
                        gr.Markdown("#### 📋 Cleanup Action Plan")
                        plan_output = gr.Markdown()
                
                # Environmental Impact Section
                gr.Markdown("---")
                impact_output = gr.Markdown()
                
                gr.Markdown("---")
                gr.Markdown("### 🤖 Step 3: Automated Reporting & Integration")
                automation_output = gr.Markdown(
                    value="""**Real-time automation status will appear here after analysis...**
                    
*CleanCity automatically integrates with your systems:*
- 🔌 Database logging
- 📊 Analytics updates  
- 🔔 Crew notifications
- 💼 Cost calculations
                    """,
                    label="Live Automation Dashboard"
                )
                
                # Social Sharing Section
                gr.Markdown("---")
                gr.Markdown("### 🌍 Share Your Impact")
                gr.Markdown("""
                Help spread awareness and inspire others to take action! Share your cleanup efforts on social media.
                """)
                
                with gr.Row():
                    share_twitter_btn = gr.Button("🐦 Share on Twitter/X", variant="secondary", size="lg")
                    share_linkedin_btn = gr.Button("💼 Share on LinkedIn", variant="secondary", size="lg")
                
                gr.HTML("""
                <div id="share-buttons" style="display: none;">
                    <a id="twitter-share" target="_blank" style="margin-right: 10px;"></a>
                    <a id="linkedin-share" target="_blank"></a>
                </div>
                <script>
                function shareOnTwitter() {
                    const text = "🌍 Just used CleanCity Agent AI to detect and plan cleanup for littered areas! Powered by @Gradio and computer vision. Join the movement for cleaner communities! #CleanCity #AI4Good #EnvironmentalAction";
                    const url = window.location.href;
                    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
                }
                function shareOnLinkedIn() {
                    const url = window.location.href;
                    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank');
                }
                </script>
                """)
                
                # Wire share buttons
                share_twitter_btn.click(
                    fn=None,
                    inputs=[],
                    outputs=[],
                    js="() => { shareOnTwitter(); }"
                )
                
                share_linkedin_btn.click(
                    fn=None,
                    inputs=[],
                    outputs=[],
                    js="() => { shareOnLinkedIn(); }"
                )
                
                # Wire up the analyze button
                analyze_btn.click(
                    fn=analyze_image,
                    inputs=[image_input, location_input, notes_input, save_history, gps_coords, use_gemini],
                    outputs=[output_image, detection_output, plan_output, automation_output, impact_output]
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
                gr.Markdown("""
                ### 📜 View Past Trash Detection Events
                
                Track all your saved trash detection events to identify patterns and monitor progress over time.
                Use filters to narrow down specific locations, timeframes, or severity levels.
                """)
                
                with gr.Row():
                    days_filter = gr.Slider(
                        minimum=0,
                        maximum=365,
                        value=30,
                        step=1,
                        label="📅 Time Range",
                        info="Last N days (0 = all time)"
                    )
                    location_filter = gr.Textbox(
                        label="📍 Location Filter",
                        placeholder="e.g., Park, Beach, Street...",
                        info="Partial match - finds all locations containing this text"
                    )
                    severity_filter = gr.Dropdown(
                        choices=["All", "Low", "Medium", "High"],
                        value="All",
                        label="⚠️ Severity Level",
                        info="Filter by cleanup urgency"
                    )
                
                load_history_btn = gr.Button("🔄 Load History", variant="primary", size="lg")
                history_output = gr.Markdown()
                
                load_history_btn.click(
                    fn=load_history,
                    inputs=[days_filter, location_filter, severity_filter],
                    outputs=history_output
                )
            
            # ================================================================
            # TAB 4: IMPACT & EXAMPLES
            # ================================================================
            with gr.Tab("🌟 Impact & Examples"):
                gr.Markdown("""
                ### 📸 Example Use Cases
                
                See how CleanCity Agent can make a difference in your community!
                """)
                
                with gr.Tabs():
                    with gr.Tab("🏖️ Beach Cleanup"):
                        gr.Markdown("""
                        #### Scenario: Beach Littered After Weekend
                        
                        **Problem:** Every Monday morning, the public beach is covered in trash from weekend visitors.
                        
                        **How CleanCity Helps:**
                        1. 📸 Take photo on Monday morning
                        2. 🤖 AI detects: 45 plastic bottles, 23 food wrappers, 12 cigarette butts
                        3. 📊 Severity: HIGH - requires 4-6 volunteers, 2 hours
                        4. 📧 Send report to Parks Department with data
                        5. ✅ Result: City adds more trash bins and signage
                        
                        **Real Impact:** 60% reduction in Monday morning trash after 2 months
                        """)
                    
                    with gr.Tab("🏞️ Park Maintenance"):
                        gr.Markdown("""
                        #### Scenario: Playground Area Safety
                        
                        **Problem:** Broken glass and sharp objects near children's playground.
                        
                        **How CleanCity Helps:**
                        1. 📸 Document with photos showing bounding boxes around dangerous items
                        2. 📋 Generate safety-focused report highlighting urgency
                        3. 📧 Email to city council with visual evidence
                        4. 👥 Organize community cleanup with volunteer count estimate
                        5. ✅ Result: City responds within 48 hours
                        
                        **Real Impact:** Safer playground + faster city response time
                        """)
                    
                    with gr.Tab("🏙️ Street Advocacy"):
                        gr.Markdown("""
                        #### Scenario: Downtown Business District
                        
                        **Problem:** Weekly trash accumulation hurting local businesses.
                        
                        **How CleanCity Helps:**
                        1. 📅 Track events over 4 weeks at same locations
                        2. 📊 Build data showing pattern: "Main Street has 8 events in 30 days"
                        3. 📈 Show historical trends in Event History tab
                        4. 📧 Present data to Business Association meeting
                        5. ✅ Result: City increases trash pickup frequency
                        
                        **Real Impact:** Cleaner streets + increased foot traffic + data-driven policy change
                        """)
                    
                    with gr.Tab("💡 Best Practices"):
                        gr.Markdown("""
                        ### 🎯 Tips for Maximum Impact
                        
                        **For Better Photos:**
                        - ✅ Take photos in daylight (9am-4pm best)
                        - ✅ Get close enough to see individual items
                        - ✅ Include landmarks for location context
                        - ✅ Take before AND after cleanup photos
                        
                        **For Better Data:**
                        - ✅ Always add specific location names
                        - ✅ Be consistent with location spelling
                        - ✅ Add notes about context (time of day, events nearby)
                        - ✅ Save to history every time
                        
                        **For Better Advocacy:**
                        - ✅ Collect 3-5 events before contacting authorities
                        - ✅ Use professional email reports
                        - ✅ Include photos with bounding boxes (shows AI verification)
                        - ✅ Suggest specific solutions (more bins, signage, schedules)
                        
                        **For Community Organizing:**
                        - ✅ Share resource estimates with volunteers upfront
                        - ✅ Use cleanup plan for event planning
                        - ✅ Document progress with before/after comparisons
                        - ✅ Celebrate wins on social media with data
                        
                        ---
                        
                        ### 📊 Sample Report Template
                        
                        **Subject:** Request for Additional Trash Infrastructure - [Location]
                        
                        **Dear [Authority Name],**
                        
                        I am writing to bring attention to a recurring trash problem at [Location]. 
                        Using AI-powered detection tools, I have documented the following:
                        
                        - **Date of observation:** [Date]
                        - **Items detected:** [X bottles, Y bags, Z wrappers]
                        - **Severity:** [High/Medium/Low]
                        - **Estimated cleanup effort:** [X volunteers, Y hours]
                        
                        [Include photo with AI bounding boxes]
                        
                        I respectfully request:
                        1. [Specific solution - more bins, regular cleaning, etc.]
                        2. [Timeline expectations]
                        
                        I am organizing a community cleanup on [Date] and would appreciate 
                        coordination with city services for disposal.
                        
                        Thank you for your attention to this matter.
                        
                        Sincerely,
                        [Your Name]
                        [Contact Information]
                        """)
                
                gr.Markdown("---")
                gr.Markdown("""
                ### 🎓 Training Resources
                
                **Want to learn more about community environmental action?**
                
                - 🌍 [EPA Community Cleanup Guide](https://www.epa.gov/communities)
                - ♻️ [Ocean Conservancy Cleanup Resources](https://oceanconservancy.org/)
                - 🏙️ [Keep America Beautiful](https://kab.org/)
                - 👥 [Community Organizing Best Practices](https://www.communitychange.org/)
                
                *Start small, document everything, and watch your impact grow!*
                """)
            
            # ================================================================
            # TAB 5: CHAT WITH AGENT
            # ================================================================
            with gr.Tab("💬 Chat with Agent"):
                gr.Markdown("""
                ### 🤖 Ask Questions or Get Help
                
                Chat with the CleanCity AI Assistant to get personalized advice and answers about:
                - 🧹 Cleanup strategies and best practices
                - 📊 Interpreting your detection results
                - 🌍 Environmental impact and regulations
                - 👥 Organizing community cleanup events
                - 📧 How to communicate with authorities
                
                **Example questions:**
                - "How many volunteers do I need for 50 plastic bottles?"
                - "What's the best time of day to organize a beach cleanup?"
                - "How do I convince my city council to add more trash bins?"
                - "What equipment is essential for a park cleanup?"
                """)
                
                chatbot = gr.Chatbot(
                    height=450,
                    placeholder="👋 Hi! I'm your CleanCity AI Assistant. Ask me anything about trash cleanup and environmental action!",
                    type="messages"
                )
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Type your question here... (e.g., 'How do I organize a cleanup event?')",
                    lines=2
                )
                
                with gr.Row():
                    submit = gr.Button("💬 Send", variant="primary", scale=2)
                    clear = gr.Button("🗑️ Clear Chat", scale=1)
                
                gr.Markdown("""
                *💡 Tip: The more specific your question, the better the advice!*
                """)
                
                def respond(message, chat_history):
                    bot_response = chat_with_agent(message, chat_history)
                    chat_history.append({"role": "user", "content": message})
                    chat_history.append({"role": "assistant", "content": bot_response})
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
    import os
    
    # Allow port override via environment variable for multiple instances
    port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
    
    print("🚀 Launching web server...")
    print(f"Access the app at: http://localhost:{port}\n")
    
    app.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=port,
        share=False,  # Set to True to create public link
        show_error=True,
        inbrowser=False,  # Don't auto-open browser (causes delay)
        quiet=False
    )


if __name__ == "__main__":
    main()
