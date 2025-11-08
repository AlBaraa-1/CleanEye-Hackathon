"""
CleanEye Streamlit Dashboard
----------------------------
Interactive interface for the ADIPEC 2025 demo. Supports image and video
uploads, live statistics from the CLI detector, and optional voice alerts.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import folium
import numpy as np
import streamlit as st
from geopy.distance import geodesic
from streamlit.components.v1 import html

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_DEFAULT_PATH = ROOT_DIR / "Weights" / "best.pt"
LOG_SUMMARY_PATH = ROOT_DIR / "outputs" / "logs" / "live_summary.json"
OUTPUTS_DIR = ROOT_DIR / "outputs"

# Simple color mapping - use raw model labels directly
COLORS = {
    "0": (0, 165, 255),           # Orange
    "c": (255, 215, 0),            # Gold
    "garbage": (0, 0, 255),        # Red
    "garbage_bag": (255, 0, 255),  # Magenta
    "waste": (0, 255, 0),          # Green
    "trash": (255, 140, 0),        # Dark Orange
}


@st.cache_resource(show_spinner=False)
def load_model(weights_path: str):
    from ultralytics import YOLO

    return YOLO(weights_path)


@st.cache_resource(show_spinner=False)
def load_voice_engine():
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        return engine
    except Exception:
        return None


def speak(engine, message: str) -> None:
    if engine is None:
        return
    engine.say(message)
    engine.runAndWait()


def ensure_outputs() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def annotate_image(model, image: np.ndarray, confidence: float) -> Dict[str, object]:
    results = model(image, conf=confidence, verbose=False)
    annotated = image.copy()
    detections: List[Dict[str, object]] = []

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        raw_label = model.names[cls_id]
        color = COLORS.get(raw_label, (255, 255, 255))
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            annotated,
            f"{raw_label} {conf:.0%}",
            (x1, max(25, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA,
        )

        detections.append(
            {
                "raw_label": raw_label,
                "label": raw_label,
                "confidence": conf,
            }
        )

    return {"image": annotated, "detections": detections}


def handle_image_upload(model, confidence: float, voice_engine) -> None:
    uploaded = st.file_uploader(
        "📁 Choose an image file", 
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG"
    )
    if not uploaded:
        # Show example/placeholder
        st.markdown("""
        #### 👆 Upload an image to get started!
        
        **What can CleanEye detect?**
        - 🗑️ General Garbage
        - 🥤 Plastic Bags & Bottles
        - 📦 Containers & Packaging
        - ♻️ Recyclable Materials
        
        Try uploading a photo of any waste and watch the AI work its magic! ✨
        """)
        return

    with st.spinner("🔍 Analyzing image..."):
        image_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        result = annotate_image(model, image, confidence)
        annotated_rgb = cv2.cvtColor(result["image"], cv2.COLOR_BGR2RGB)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📷 Original Image")
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)
    with col2:
        st.markdown("#### 🎯 AI Detection Results")
        st.image(annotated_rgb, use_container_width=True)

    detections = result["detections"]
    
    st.markdown("---")
    
    if detections:
        st.success(f"✅ **Found {len(detections)} garbage item(s)!**")
        
        # Show detections in a nice format
        st.markdown("#### 🗑️ Detected Items:")
        
        # Create columns for better layout
        cols = st.columns(min(3, len(detections)))
        for idx, det in enumerate(detections):
            with cols[idx % 3]:
                confidence_pct = det['confidence'] * 100
                st.metric(
                    label=det['label'],
                    value=f"{confidence_pct:.0f}%"
                )
        
        # Save button
        if st.button("💾 Save Results", type="primary"):
            ensure_outputs()
            output_path = OUTPUTS_DIR / f"streamlit_image_{uploaded.name}"
            cv2.imwrite(str(output_path), result["image"])
            st.success(f"✅ Saved to: `{output_path.name}`")
        
        if st.session_state.voice_enabled:
            speak(voice_engine, f"Detected {len(detections)} garbage items.")
    else:
        st.warning("⚠️ **No garbage detected in this image.**")
        st.info("""
        **Try these tips:**
        - 🔽 Lower the detection sensitivity slider
        - 📸 Use a clearer or closer photo
        - 💡 Make sure the image has visible waste
        """)


def handle_video_upload(model, confidence: float, voice_engine) -> None:
    uploaded = st.file_uploader(
        "📁 Choose a video file", 
        type=["mp4", "mov", "avi"], 
        key="video_uploader",
        help="Supported formats: MP4, MOV, AVI"
    )
    if not uploaded:
        st.markdown("""
        #### 👆 Upload a video to analyze!
        
        **How it works:**
        1. Upload your video file
        2. Our AI analyzes each frame
        3. Get instant statistics on detected waste
        
        💡 **Tip:** Shorter videos (under 30 seconds) process faster!
        """)
        return

    with st.spinner("🎬 Processing video... This may take a moment."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded.getbuffer())
            temp_path = Path(tmp_file.name)

    cap = cv2.VideoCapture(str(temp_path))
    if not cap.isOpened():
        st.error("❌ Unable to open video file. Please try another format.")
        temp_path.unlink(missing_ok=True)
        return

    frames_analyzed = 0
    detections_found = 0
    unique_items = set()

    st.markdown("#### 🎥 Video Analysis in Progress...")
    progress_bar = st.progress(0)
    st_frame = st.empty()
    stats_placeholder = st.empty()
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            frames_analyzed += 1
            result = annotate_image(model, frame, confidence)
            
            if result["detections"]:
                detections_found += len(result["detections"])
                for det in result["detections"]:
                    unique_items.add(det["label"])
                    
                if st.session_state.voice_enabled and detections_found == len(result["detections"]):
                    speak(voice_engine, "Garbage detected in video.")

            frame_rgb = cv2.cvtColor(result["image"], cv2.COLOR_BGR2RGB)
            st_frame.image(frame_rgb, use_container_width=True)
            
            # Update progress
            progress = min(frames_analyzed / st.session_state.video_frame_limit, 1.0)
            progress_bar.progress(progress)
            
            # Update stats
            stats_placeholder.metric(
                "Detections So Far", 
                detections_found,
                f"Frame {frames_analyzed}"
            )

            if frames_analyzed >= st.session_state.video_frame_limit:
                break
    finally:
        cap.release()
        temp_path.unlink(missing_ok=True)

    # Final results
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
    else:
        st.info("ℹ️ No garbage detected in this video. Try lowering the sensitivity or use a different video.")


def load_detection_summary() -> Optional[Dict[str, object]]:
    if not LOG_SUMMARY_PATH.exists():
        return None
    try:
        with LOG_SUMMARY_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return None


def render_live_statistics(summary: Optional[Dict[str, object]], voice_engine) -> None:
    if not summary:
        st.warning("📡 **No live data available yet.**")
        st.info("""
        **How to enable live detection:**
        
        Run this command in your terminal:
        ```bash
        python code/detect_pro.py
        ```
        
        Once running, come back here and click the refresh button to see live statistics! 📊
        """)
        return

    total = summary.get("total_detections", 0)
    
    # Big metric at the top
    st.metric(
        "🗑️ Total Garbage Detected", 
        total,
        help="Total items detected by live detection system"
    )

    if total and st.session_state.voice_enabled and summary != st.session_state.get("last_summary"):
        speak(voice_engine, "New garbage detected by live system.")

    st.session_state["last_summary"] = summary
    
    st.markdown("---")

    # Class breakdown
    class_counts = summary.get("class_counts", {})
    if class_counts:
        st.markdown("### 🗂️ Breakdown by Type")
        
        # Create a nice chart
        import pandas as pd
        df = pd.DataFrame([
            {"Type": label, "Count": count} 
            for label, count in class_counts.items()
        ])
        st.bar_chart(df.set_index("Type"))
        
        # Also show as list
        with st.expander("📋 View Detailed List"):
            for label, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                st.write(f"**{label}:** {count} items ({percentage:.1f}%)")

    # Location info
    st.markdown("---")
    location_hint = summary.get("location_hint")
    if location_hint:
        lat = location_hint.get("latitude")
        lon = location_hint.get("longitude")
        if lat is not None and lon is not None:
            st.markdown("### 📍 Detection Location")
            st.write(f"**Coordinates:** {lat:.5f}, {lon:.5f}")
            render_map(lat, lon)
    
    # Last update time
    updated = summary.get("updated_at", "Unknown")
    st.caption(f"📅 Last updated: {updated}")


def render_map(latitude: float, longitude: float) -> None:
    venue = (24.4181, 54.4583)
    distance = geodesic(venue, (latitude, longitude)).meters
    
    st.success(f"📏 **Distance from booth:** {distance:.0f} meters")

    fmap = folium.Map(location=[latitude, longitude], zoom_start=16, tiles="CartoDB positron")
    
    # Detection marker (red)
    folium.Marker(
        location=[latitude, longitude],
        popup="🗑️ Latest Garbage Detection",
        tooltip="Click for details",
        icon=folium.Icon(color="red", icon="trash", prefix="fa"),
    ).add_to(fmap)
    
    # Booth marker (green)
    folium.Marker(
        location=list(venue),
        popup="🏢 CleanEye Booth - ADNEC",
        tooltip="ADIPEC 2025 Venue",
        icon=folium.Icon(color="green", icon="info-sign"),
    ).add_to(fmap)

    html(fmap._repr_html_(), height=400)


def main() -> None:
    st.set_page_config(
        page_title="CleanEye - ADIPEC Demo", 
        layout="wide",
        page_icon="🗑️"
    )
    
    # Header with emoji and clear description
    st.markdown("# 🗑️ CleanEye - Smart Garbage Detection")
    st.markdown("### 🤖 AI-Powered Waste Detection for a Cleaner Tomorrow")
    st.markdown("---")
    
    # Welcome message with instructions
    st.info("""
    👋 **Welcome to CleanEye!** Here's how it works:
    
    1. 📸 **Upload an image** to detect garbage in photos
    2. 🎥 **Upload a video** to analyze waste in motion
    3. 📊 **View live statistics** from our detection system
    
    🎯 Our AI can identify different types of waste and help keep Abu Dhabi clean!
    """)

    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown("Adjust how the AI detects garbage")
        st.markdown("---")
        
        with st.expander("🎯 Detection Settings", expanded=True):
            confidence = st.slider(
                "Detection Sensitivity", 
                0.1, 0.9, 0.25, 0.05,
                help="Lower = More detections (may include false positives). Higher = Only obvious garbage."
            )
            
            # Visual feedback for confidence level
            if confidence < 0.3:
                st.success("🔍 **High Sensitivity** - Detects more objects")
            elif confidence < 0.5:
                st.info("⚖️ **Balanced** - Recommended setting")
            else:
                st.warning("🎯 **Strict Mode** - Only confident detections")
        
        st.markdown("---")
        
        with st.expander("🔊 Advanced Options"):
            st.session_state.voice_enabled = st.checkbox(
                "🔊 Voice Alerts", 
                value=False,
                help="Hear audio notifications when garbage is detected"
            )
            st.session_state.video_frame_limit = st.slider(
                "Video frames to analyze", 
                30, 600, 180, 30,
                help="More frames = slower but more thorough analysis"
            )
        
        st.markdown("---")
        st.markdown("### 📖 Quick Guide")
        st.markdown("""
        **For Best Results:**
        - 📸 Use clear, well-lit photos
        - 🗑️ Make sure garbage is visible
        - 🎥 Videos work best at normal speed
        - ⚡ Lower sensitivity for small items
        """)
        
        st.markdown("---")
        st.caption("💡 Tip: Run 'detect_pro.py' for live camera feed")

        weights_path = str(MODEL_DEFAULT_PATH)  # Hidden, use default

    model = load_model(weights_path)
    voice_engine = load_voice_engine() if st.session_state.voice_enabled else None

    tabs = st.tabs(["📸 Upload Image", "🎥 Upload Video", "📊 Live Statistics"])

    with tabs[0]:
        st.markdown("### 📸 Image Detection")
        st.markdown("Upload a photo and let our AI find any garbage in it!")
        handle_image_upload(model, confidence, voice_engine)
        
    with tabs[1]:
        st.markdown("### 🎥 Video Detection")
        st.markdown("Upload a video to analyze waste over time!")
        handle_video_upload(model, confidence, voice_engine)
        
    with tabs[2]:
        st.markdown("### 📊 Real-Time Statistics")
        st.markdown("See live data from our detection system running in Abu Dhabi!")
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
        summary = load_detection_summary()
        render_live_statistics(summary, voice_engine)


if __name__ == "__main__":
    main()
