"""
CleanEye Streamlit Dashboard - Cloud Optimized
----------------------------------------------
Optimized for Hugging Face Spaces and Streamlit Cloud deployment.
Interactive interface for garbage detection demo.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
import streamlit as st

# Cloud-compatible paths
ROOT_DIR = Path(__file__).resolve().parent
MODEL_PATH = ROOT_DIR / "Weights" / "best.pt"

# Fallback if Weights folder doesn't exist at same level
if not MODEL_PATH.exists():
    MODEL_PATH = Path(__file__).resolve().parent.parent / "Weights" / "best.pt"

# Simple color mapping
COLORS = {
    "0": (0, 165, 255),           # Orange
    "c": (255, 215, 0),            # Gold
    "garbage": (0, 0, 255),        # Red
    "garbage_bag": (255, 0, 255),  # Magenta
    "waste": (0, 255, 0),          # Green
    "trash": (255, 140, 0),        # Dark Orange
}


@st.cache_resource(show_spinner=False)
def load_model():
    """Load YOLOv8 model with caching"""
    from ultralytics import YOLO
    
    if not MODEL_PATH.exists():
        st.error(f"Model not found at {MODEL_PATH}")
        st.stop()
    
    try:
        model = YOLO(str(MODEL_PATH))
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()


def annotate_image(model, image: np.ndarray, confidence: float) -> Dict:
    """Run detection and annotate image"""
    results = model(image, conf=confidence, verbose=False)
    annotated = image.copy()
    detections: List[Dict] = []

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = model.names[cls_id]
        color = COLORS.get(label, (255, 255, 255))
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        cv2.putText(
            annotated,
            f"{label} {conf:.0%}",
            (x1, max(25, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA,
        )

        detections.append({
            "label": label,
            "confidence": conf,
            "bbox": [x1, y1, x2, y2]
        })

    return {"image": annotated, "detections": detections}


def calculate_severity(detections: List[Dict], image_shape: tuple) -> Dict:
    """Calculate waste severity level"""
    count = len(detections)
    h, w = image_shape[:2]
    image_area = h * w
    
    # Calculate total detection area
    total_detection_area = 0
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        total_detection_area += (x2 - x1) * (y2 - y1)
    
    # Calculate coverage percentage
    coverage = (total_detection_area / image_area * 100) if image_area > 0 else 0
    
    # Determine severity
    if count == 0:
        level = "🟢 Clean"
        color = "green"
        recommendation = "Area appears clean. Regular monitoring recommended."
    elif count < 3 or coverage < 5:
        level = "🟡 Light"
        color = "orange"
        recommendation = "Minor waste detected. Schedule routine cleanup."
    elif count < 8 or coverage < 15:
        level = "🟠 Moderate"
        color = "orange"
        recommendation = "Moderate waste detected. Schedule cleanup within 24-48 hours."
    else:
        level = "🔴 Severe"
        color = "red"
        recommendation = "High waste concentration! Immediate cleanup required."
    
    return {
        "level": level,
        "color": color,
        "count": count,
        "coverage": coverage,
        "recommendation": recommendation
    }


def main():
    """Main Streamlit app"""
    
    # Page configuration
    st.set_page_config(
        page_title="CleanEye - AI Garbage Detection",
        page_icon="🗑️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #2E7D32;
            text-align: center;
            margin-bottom: 0;
        }
        .sub-header {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stButton>button {
            width: 100%;
            background-color: #2E7D32;
            color: white;
        }
        /* Center Streamlit tab labels */
        div[data-baseweb="tab-list"] {
            justify-content: center !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🗑️ CleanEye</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-Powered Garbage Detection for Smart Cities | Built for MCP Hackathon</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/ultralytics/assets/main/logo/Ultralytics_Logotype_Original.svg", width=200)
        st.markdown("---")
        
        st.markdown("### 🎯 About CleanEye")
        st.info(
            "CleanEye uses YOLOv8 trained on 4000+ images to detect and classify "
            "urban waste in real-time. Built for the **MCP 1st Birthday Hackathon**."
        )
        
        st.markdown("### ⚙️ Detection Settings")
        confidence = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05,
            help="Higher values = fewer but more confident detections"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Waste Categories")
        categories = [
            "🟠 General Waste (0)",
            "🔴 Garbage",
            "🟣 Garbage Bags"
        ]
        for cat in categories:
            st.markdown(f"- {cat}")
        
        st.markdown("---")
        st.markdown("### 🔗 Links")
        st.markdown("- [GitHub Repo](https://github.com/AlBaraa-1/Computer-vision)")
        st.markdown("- [MCP Documentation](https://github.com/AlBaraa-1/Computer-vision/tree/main/CleanEye)")
        st.markdown("- [Hackathon Info](https://huggingface.co/spaces/Gradio-Blocks/mcp-1st-birthday)")
        
        st.markdown("---")
        st.markdown("**Developer:** AlBaraa AlOlabi (@AlBaraa63)")
        st.markdown("**Track:** MCP in Action (Agents)")
        st.markdown("---")
        st.markdown("### 🧪 Test Samples")
        st.info("Download and try these sample images:")
        sample_dir = ROOT_DIR / "test_samples"
        sample_files = [
            ("sample_1_bins.jpg", "Garbage and recycle bins"),
            ("sample_2_bags.jpg", "Black garbage bags"),
            ("sample_3_pile.jpg", "Large garbage pile"),
            ("sample_4_street.jpg", "Street waste scenario"),
            ("sample_5_plastic.jpg", "Plastic waste accumulation")
        ]
        for fname, desc in sample_files:
            fpath = sample_dir / fname
            if fpath.exists():
                with open(fpath, "rb") as f:
                    btn_label = f"⬇️ {desc}"
                    st.download_button(btn_label, f.read(), file_name=fname, mime="image/jpeg")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📸 Image Detection", "🎥 Video Detection", "📊 About", "🏆 Hackathon"])
    
    with tab1:
        st.markdown("### Upload an Image for Detection")
        
        uploaded_file = st.file_uploader(
            "Choose an image (JPG, PNG, JPEG)",
            type=["jpg", "jpeg", "png"],
            help="Upload an image containing garbage or waste"
        )
        
        if uploaded_file is not None:
            # Read and display original image
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Original Image")
                st.image(image_rgb, use_container_width=True)
            
            # Run detection
            with st.spinner("🔍 Detecting garbage..."):
                model = load_model()
                result = annotate_image(model, image, confidence)
                
                # Calculate severity
                severity = calculate_severity(result["detections"], image.shape)
            
            with col2:
                st.markdown("#### Detection Results")
                annotated_rgb = cv2.cvtColor(result["image"], cv2.COLOR_BGR2RGB)
                st.image(annotated_rgb, use_container_width=True)
            
            # Display statistics
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Detections", severity["count"])
            
            with col2:
                st.metric("Coverage", f"{severity['coverage']:.1f}%")
            
            with col3:
                st.metric("Severity", severity["level"])
            
            with col4:
                avg_conf = np.mean([d["confidence"] for d in result["detections"]]) if result["detections"] else 0
                st.metric("Avg Confidence", f"{avg_conf:.0%}")
            
            # Severity assessment
            st.markdown(f"### {severity['level']} Assessment")
            if severity["color"] == "green":
                st.success(severity["recommendation"])
            elif severity["color"] == "orange":
                st.warning(severity["recommendation"])
            else:
                st.error(severity["recommendation"])
            
            # Category breakdown
            if result["detections"]:
                st.markdown("### 🏷️ Category Breakdown")
                
                category_counts = {}
                for det in result["detections"]:
                    label = det["label"]
                    category_counts[label] = category_counts.get(label, 0) + 1
                
                cols = st.columns(len(category_counts))
                for idx, (category, count) in enumerate(category_counts.items()):
                    with cols[idx]:
                        st.metric(category.title(), count)
                
                # Detailed detections table
                with st.expander("📋 View Detailed Detections"):
                    for idx, det in enumerate(result["detections"], 1):
                        st.markdown(
                            f"**Detection {idx}:** {det['label']} "
                            f"({det['confidence']:.1%} confidence)"
                        )
            else:
                st.info("No garbage detected in this image! 🎉")
        
        else:
            # Show example placeholder
            st.info("👆 Upload an image to start detecting garbage")
            st.markdown("#### 💡 Tips for Best Results:")
            st.markdown("""
            - Use clear, well-lit images
            - Ensure garbage is visible and not too far away
            - Multiple items can be detected in a single image
            - Adjust confidence threshold if needed (sidebar)
            """)
    
    with tab2:
        st.markdown("### Upload a Video for Detection")
        
        uploaded_video = st.file_uploader(
            "Choose a video file (MP4, MOV, AVI)",
            type=["mp4", "mov", "avi"],
            help="Upload a video to analyze garbage frame-by-frame"
        )
        
        if uploaded_video is not None:
            # Save uploaded video temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(uploaded_video.getbuffer())
                temp_path = Path(tmp_file.name)
            
            # Open video
            cap = cv2.VideoCapture(str(temp_path))
            
            if not cap.isOpened():
                st.error("❌ Unable to open video file. Please try another format.")
                temp_path.unlink(missing_ok=True)
                return
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            st.info(f"📹 Video Info: {total_frames} frames at {fps} FPS")
            
            # Limit frames to analyze for cloud deployment
            max_frames = st.slider("Maximum frames to analyze", 10, 200, 100,
                                  help="Analyzing fewer frames is faster")
            
            # Analysis button
            if st.button("🎬 Start Analysis"):
                model = load_model()
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                video_frame_placeholder = st.empty()
                
                frames_analyzed = 0
                detections_found = 0
                unique_items = set()
                detection_samples = []
                annotated_frames = []
                
                # Process video frames
                frame_skip = max(1, total_frames // max_frames)
                
                # Reset video to start
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
                try:
                    while frames_analyzed < max_frames:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        # Skip frames for efficiency
                        for _ in range(frame_skip - 1):
                            cap.read()
                        
                        # Run detection
                        results = model(frame, conf=confidence, verbose=False)
                        
                        # Annotate frame
                        annotated = frame.copy()
                        frame_detections = len(results[0].boxes)
                        
                        if frame_detections > 0:
                            detections_found += frame_detections
                            
                            # Draw detections
                            for box in results[0].boxes:
                                cls_id = int(box.cls[0])
                                conf_score = float(box.conf[0])
                                label = model.names[cls_id]
                                color = COLORS.get(label, (255, 255, 255))
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                
                                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                                cv2.putText(annotated, f"{label} {conf_score:.0%}", 
                                          (x1, max(25, y1 - 10)),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                                
                                unique_items.add(label)
                            
                            # Save sample detection frames (first 5)
                            if len(detection_samples) < 5:
                                detection_samples.append(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
                        
                        # Show current frame being processed
                        if frames_analyzed % 10 == 0:  # Update display every 10 frames
                            frame_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                            video_frame_placeholder.image(frame_rgb, caption=f"Processing frame {frames_analyzed}...", 
                                                        use_container_width=True)
                        
                        # Store frames for optional video output (limit to 30 for performance)
                        if len(annotated_frames) < 30:
                            annotated_frames.append(annotated)
                        
                        frames_analyzed += 1
                        progress = frames_analyzed / max_frames
                        progress_bar.progress(progress)
                        status_text.text(f"Analyzing... {frames_analyzed}/{max_frames} frames | Detections: {detections_found}")
                
                finally:
                    cap.release()
                    temp_path.unlink(missing_ok=True)
                
                # Clear processing display
                video_frame_placeholder.empty()
                
                # Display results
                st.markdown("---")
                st.markdown("### 📊 Video Analysis Complete!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📹 Frames Analyzed", frames_analyzed)
                
                with col2:
                    st.metric("🗑️ Total Detections", detections_found)
                
                with col3:
                    avg = detections_found / frames_analyzed if frames_analyzed > 0 else 0
                    st.metric("📈 Avg per Frame", f"{avg:.2f}")
                
                if unique_items:
                    st.success(f"✅ **Found {len(unique_items)} different types of garbage:**")
                    st.write(", ".join(f"🗑️ {item}" for item in sorted(unique_items)))
                    
                    # Show sample detection frames
                    if detection_samples:
                        st.markdown("### 🖼️ Sample Detection Frames")
                        st.markdown(f"*Showing {len(detection_samples)} frames with detections*")
                        
                        # Display in rows of 3
                        for i in range(0, len(detection_samples), 3):
                            cols = st.columns(3)
                            for idx, img in enumerate(detection_samples[i:i+3]):
                                with cols[idx]:
                                    st.image(img, caption=f"Sample {i+idx+1}", use_container_width=True)
                    
                    # Create a short video clip if we have frames
                    if annotated_frames and len(annotated_frames) >= 10:
                        st.markdown("### 🎬 Annotated Video Sample")
                        st.info(f"📹 Showing first {len(annotated_frames)} processed frames as a video sample")
                        
                        # Create temporary video file with better codec
                        output_video_path = Path(tempfile.gettempdir()) / f"detection_output_{hash(str(annotated_frames[0].data.tobytes()))}.mp4"
                        
                        # Get frame dimensions
                        height, width = annotated_frames[0].shape[:2]
                        
                        try:
                            # Try H.264 codec (better browser compatibility)
                            fourcc = cv2.VideoWriter_fourcc(*'avc1')
                            out = cv2.VideoWriter(str(output_video_path), fourcc, 10.0, (width, height))
                            
                            # If that fails, fallback to mp4v
                            if not out.isOpened():
                                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                                out = cv2.VideoWriter(str(output_video_path), fourcc, 10.0, (width, height))
                            
                            for frame in annotated_frames:
                                out.write(frame)
                            
                            out.release()
                            
                            # Check if video file was created successfully
                            if output_video_path.exists() and output_video_path.stat().st_size > 0:
                                # Display video
                                with open(output_video_path, 'rb') as video_file:
                                    video_bytes = video_file.read()
                                    st.video(video_bytes)
                                
                                # Cleanup
                                output_video_path.unlink(missing_ok=True)
                            else:
                                st.warning("⚠️ Could not create video file. Showing frames as slideshow instead.")
                                # Show as image slideshow
                                st.markdown("#### 📸 Detection Frames Slideshow")
                                frame_placeholder = st.empty()
                                import time
                                for idx, frame in enumerate(annotated_frames):
                                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    frame_placeholder.image(frame_rgb, caption=f"Frame {idx+1}/{len(annotated_frames)}", 
                                                          use_container_width=True)
                                    time.sleep(0.1)  # 10 FPS
                        
                        except Exception as e:
                            st.warning(f"⚠️ Video creation failed: {str(e)}. Showing sample frames instead.")
                            # Fallback: show frames in a grid
                            st.markdown("#### 📸 All Detection Frames")
                            for i in range(0, len(annotated_frames), 3):
                                cols = st.columns(3)
                                for idx, frame in enumerate(annotated_frames[i:i+3]):
                                    with cols[idx]:
                                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                        st.image(frame_rgb, caption=f"Frame {i+idx+1}", use_container_width=True)
                        
                else:
                    st.info("ℹ️ No garbage detected in this video. Try lowering the confidence threshold.")
        
        else:
            st.info("👆 Upload a video to start analyzing")
            st.markdown("#### 💡 Video Analysis Tips:")
            st.markdown("""
            - Shorter videos process faster
            - Clear, stable footage works best
            - Good lighting improves detection accuracy
            - The system analyzes frames at regular intervals
            """)
    
    with tab4:
        st.markdown("## 🎯 About CleanEye")
        
        st.markdown("""
        **CleanEye** is an MCP-enabled AI agent for real-time garbage detection and 
        smart city monitoring. It uses YOLOv8 computer vision to identify and classify 
        urban waste, helping cities optimize cleanup operations and reduce environmental impact.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 Key Features")
            st.markdown("""
            - ✅ **6 Waste Categories** detected
            - ✅ **Real-time Detection** (<1 second)
            - ✅ **85%+ Accuracy** on test set
            - ✅ **4000+ Training Images**
            - ✅ **MCP Integration** for AI agents
            - ✅ **Severity Assessment** algorithm
            """)
        
        with col2:
            st.markdown("### 🌍 Use Cases")
            st.markdown("""
            - 🏙️ Smart city waste monitoring
            - 🤖 Autonomous cleanup robots
            - 📱 Citizen reporting apps
            - 📊 Environmental compliance
            - 🗺️ Waste mapping systems
            - 🚛 Optimized collection routes
            """)
        
        st.markdown("---")
        st.markdown("### 🏗️ Technology Stack")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Computer Vision**")
            st.markdown("- YOLOv8 (Ultralytics)")
            st.markdown("- OpenCV")
            st.markdown("- PyTorch")
        
        with col2:
            st.markdown("**Agent Framework**")
            st.markdown("- Model Context Protocol (MCP)")
            st.markdown("- 4 Agent-callable tools")
            st.markdown("- LLM integration ready")
        
        with col3:
            st.markdown("**Deployment**")
            st.markdown("- Streamlit Dashboard")
            st.markdown("- Hugging Face Spaces")
            st.markdown("- Python 3.12")
    
    with tab3:
        st.markdown("## 🏆 MCP 1st Birthday Hackathon")
        
        st.markdown("""
        This project was built for the **MCP 1st Birthday Hackathon** 
        (November 14-30, 2025), hosted by Anthropic and Gradio.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Track Selection")
            st.info("**Track 2: MCP in Action (Agents)**")
            st.markdown("""
            CleanEye demonstrates how AI agents can sense and act in the real world 
            through computer vision, combining perception with decision-making for 
            environmental sustainability.
            """)
        
        with col2:
            st.markdown("### 💡 Innovation")
            st.markdown("""
            - First garbage detection system with MCP
            - Agent-to-agent communication via MCP tools
            - Real environmental impact potential
            - Scalable to entire smart city networks
            """)
        
        st.markdown("---")
        
        st.markdown("### 🔌 MCP Tools Available")
        st.markdown("""
        CleanEye exposes 4 MCP tools that AI agents can call:
        
        1. **`detect_garbage_image`** - Detect garbage in images with bounding boxes
        2. **`get_detection_statistics`** - Access real-time detection stats
        3. **`analyze_area_severity`** - Assess cleanup priority levels
        4. **`get_detection_reports`** - Retrieve historical detection data
        """)
        
        st.markdown("### 📊 Project Impact")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Training Images", "4,000+")
        
        with col2:
            st.metric("Model Accuracy", "85%+")
        
        with col3:
            st.metric("Detection Speed", "<1 sec")
        
        st.markdown("---")
        
        st.markdown("### 👨‍💻 Developer")
        st.markdown("""
        **AlBaraa AlOlabi**
        - 🤗 Hugging Face: [@AlBaraa63](https://huggingface.co/AlBaraa63)
        - 💻 GitHub: [@AlBaraa-1](https://github.com/AlBaraa-1)
        - 📧 Email: 666645@gmail.com
        """)
        
        st.markdown("---")
        st.success("🌍 Making cities cleaner with AI agents!")


if __name__ == "__main__":
    main()
