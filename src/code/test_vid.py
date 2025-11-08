"""
CleanEye - Video Tester
Test garbage detection on video files
"""
import cv2
from ultralytics import YOLO
import os

# Simple color mapping - use raw model labels directly
COLORS = {
    "0": (0, 165, 255),           # Orange
    "c": (255, 215, 0),            # Gold
    "garbage": (0, 0, 255),        # Red
    "garbage_bag": (255, 0, 255),  # Magenta
    "waste": (0, 255, 0),          # Green
    "trash": (255, 140, 0),        # Dark Orange
}
def test_video(video_path="media/garbage.mp4", confidence_threshold=0.25):
    """
    Test garbage detection on a video file
    
    Args:
        video_path: Path to video file
        confidence_threshold: Minimum confidence for detection
    """
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Error: Video not found at {video_path}")
        print("\n📁 Available videos in media/:")
        if os.path.exists('media'):
            for file in os.listdir('media'):
                if file.lower().endswith(('.mp4', '.avi', '.mov')):
                    print(f"  - {file}")
        return False
    
    # Load YOLO model with custom weights
    print("🔄 Loading model from Weights/best.pt...")
    model = YOLO("Weights/best.pt")
    print("✅ Model loaded successfully!\n")
    
    # Initialize video capture
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: Could not open video {video_path}")
        return False
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"🎥 Video loaded: {os.path.basename(video_path)}")
    print(f"📐 Resolution: {width}x{height}")
    print(f"🎞️  FPS: {fps}")
    print(f"⏱️  Frames: {total_frames} (~{total_frames//fps} seconds)")
    print(f"🔍 Detection threshold: {confidence_threshold}")
    print("\n💡 Controls:")
    print("  - Press 'q' to quit")
    print("  - Press 'SPACE' to pause/resume")
    print("  - Press 's' to save frame")
    print("  - Press '+' to speed up (up to 4x)")
    print("  - Press '-' to slow down (down to 0.5x)")
    print("  - Press 'f' to toggle fast mode (skip frames)\n")
    
    frame_count = 0
    total_detections = 0
    paused = False
    skip_frames = 1  # Process every frame by default (1 = no skip)
    playback_speed = 1.0  # 1.0 = normal speed
    
    while True:
        if not paused:
            success, img = cap.read()
            
            if not success:
                print("\n✅ Video ended!")
                break
            
            frame_count += 1
            
            # Skip frames for faster processing
            if frame_count % skip_frames != 0:
                continue
            
            # Run detection
            results = model(img, conf=confidence_threshold, verbose=False)
            
            detection_in_frame = 0
            
            # Process each detection
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                raw_label = model.names[cls_id]
                color = COLORS.get(raw_label, (255, 255, 255))
                
                if conf >= confidence_threshold:
                    detection_in_frame += 1
                    total_detections += 1
                    
                    # Draw bounding box (consistent with other scripts)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        img,
                        f"{raw_label} {conf:.0%}",
                        (x1, max(25, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        color,
                        2,
                        cv2.LINE_AA,
                    )
            
            # Add frame info overlay
            info_text = f"Frame: {frame_count}/{total_frames} | Detections: {detection_in_frame}"
            cv2.putText(img, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display
        cv2.imshow("CleanEye - Video Detection", img)
        
        # Handle key presses with adjustable playback speed
        # Calculate delay based on FPS and playback speed
        delay = max(1, int((1000 / fps) / playback_speed)) if fps > 0 else 1
        key = cv2.waitKey(delay) & 0xFF
        
        if key == ord('q'):
            print("\n🛑 Stopped by user")
            break
        elif key == ord(' '):  # Space bar
            paused = not paused
            if paused:
                print("⏸️  Paused")
            else:
                print("▶️  Resumed")
        elif key == ord('s'):
            # Save current frame
            output_path = f"outputs/video_frame_{frame_count}.jpg"
            os.makedirs("outputs", exist_ok=True)
            cv2.imwrite(output_path, img)
            print(f"💾 Saved: {output_path}")
        elif key in (ord('+'), ord('=')):  # Speed up
            playback_speed = min(4.0, playback_speed + 0.5)
            print(f"⚡ Speed: {playback_speed}x")
        elif key == ord('-'):  # Slow down
            playback_speed = max(0.5, playback_speed - 0.5)
            print(f"🐢 Speed: {playback_speed}x")
        elif key == ord('f'):  # Toggle frame skip
            skip_frames = 2 if skip_frames == 1 else 1
            mode = "FAST (skip frames)" if skip_frames == 2 else "NORMAL (all frames)"
            print(f"🎬 Mode: {mode}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    # Show statistics
    print("\n" + "=" * 70)
    print("📊 Video Detection Summary")
    print("=" * 70)
    print(f"✅ Frames processed: {frame_count}/{total_frames}")
    print(f"🗑️  Total detections: {total_detections}")
    print(f"📈 Avg detections/frame: {total_detections/frame_count:.2f}")
    print("=" * 70)
    
    return True
def main():
    print("=" * 70)
    print("🗑️  CleanEye - Video Tester")
    print("=" * 70)
    
    # Get available videos
    video_files = []
    if os.path.exists('media'):
        for file in os.listdir('media'):
            if file.lower().endswith(('.mp4', '.avi', '.mov')):
                video_files.append(file)
    
    if not video_files:
        print("\n❌ No video files found in 'media/' folder")
        print("💡 Add .mp4, .avi, or .mov files to test!")
        return
    
    print(f"\n📁 Found {len(video_files)} video file(s):\n")
    
    for i, vid in enumerate(video_files, 1):
        print(f"  [{i}] {vid}")
    
    print(f"  [q] Quit")
    
    # Get user choice
    print()
    choice = input("Select video to test: ").strip().lower()
    
    if choice == 'q':
        print("👋 Goodbye!")
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(video_files):
            video_path = os.path.join("media", video_files[index])
            test_video(video_path)
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Invalid input!")
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
