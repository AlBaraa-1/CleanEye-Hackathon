"""
CleanEye - Detection with Before/After Report
Generates detailed reports with statistics and unique IDs
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
from ultralytics import YOLO

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = ROOT_DIR / "Weights" / "best.pt"
REPORTS_DIR = ROOT_DIR / "outputs" / "reports"
MEDIA_DIR = ROOT_DIR / "media"

# Simple color mapping
COLORS = {
    "0": (0, 165, 255),
    "c": (255, 215, 0),
    "garbage": (0, 0, 255),
    "garbage_bag": (255, 0, 255),
    "waste": (0, 255, 0),
    "trash": (255, 140, 0),
}


class DetectionReport:
    """Generate before/after detection reports with statistics"""
    
    def __init__(self, model_path: Path, confidence: float = 0.25):
        self.model_path = model_path
        self.confidence = confidence
        self.model = None
        self.report_id = None
        self.detections: List[Dict] = []
        
    def load_model(self) -> bool:
        """Load YOLO model"""
        try:
            print(f"[INFO] Loading model from {self.model_path}...")
            self.model = YOLO(str(self.model_path))
            print("[INFO] Model ready.")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return False
    
    def detect(self, image_path: Path) -> Dict:
        """Run detection and collect statistics"""
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"Unable to read image: {image_path}")
        
        # Run detection
        results = self.model(image, conf=self.confidence, verbose=False)
        boxes = results[0].boxes
        
        # Collect detections
        detections = []
        class_counts = {}
        
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = self.model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            detections.append({
                "label": label,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })
            
            class_counts[label] = class_counts.get(label, 0) + 1
        
        return {
            "image_path": str(image_path),
            "total_detections": len(detections),
            "class_counts": class_counts,
            "detections": detections,
            "image_size": {"width": image.shape[1], "height": image.shape[0]}
        }
    
    def annotate_image(self, image_path: Path, save_path: Path) -> np.ndarray:
        """Annotate image with detections"""
        image = cv2.imread(str(image_path))
        results = self.model(image, conf=self.confidence, verbose=False)
        
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = self.model.names[cls_id]
            color = COLORS.get(label, (255, 255, 255))
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Draw box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                image,
                f"{label} {conf:.0%}",
                (x1, max(25, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
                cv2.LINE_AA,
            )
        
        # Save annotated image
        cv2.imwrite(str(save_path), image)
        return image
    
    def generate_report(self, image_path: Path, output_name: str = None) -> str:
        """Generate comprehensive before/after report"""
        
        # Generate report ID
        self.report_id = f"CLN-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create report directory
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_dir = REPORTS_DIR / self.report_id
        report_dir.mkdir(exist_ok=True)
        
        print("\n" + "=" * 80)
        print(f"📋 CLEANEYE DETECTION REPORT")
        print("=" * 80)
        print(f"Report ID: {self.report_id}")
        print(f"Timestamp: {timestamp}")
        print(f"Image: {image_path.name}")
        print("=" * 80)
        
        # BEFORE: Show original image
        print("\n📸 BEFORE DETECTION:")
        print("   Status: Analyzing image for waste...")
        print(f"   Image Size: {cv2.imread(str(image_path)).shape[1]}x{cv2.imread(str(image_path)).shape[0]} pixels")
        
        # Save original image
        before_path = report_dir / f"before_{image_path.name}"
        original = cv2.imread(str(image_path))
        cv2.imwrite(str(before_path), original)
        print(f"   Saved: {before_path.name}")
        
        # Run detection
        print("\n🔍 RUNNING AI DETECTION...")
        detection_data = self.detect(image_path)
        
        # AFTER: Annotate and save
        after_path = report_dir / f"after_{image_path.name}"
        self.annotate_image(image_path, after_path)
        
        print("\n🎯 AFTER DETECTION:")
        print(f"   Status: Detection complete!")
        print(f"   Saved: {after_path.name}")
        
        # Statistics
        total = detection_data["total_detections"]
        print("\n" + "=" * 80)
        print("📊 DETECTION STATISTICS")
        print("=" * 80)
        
        if total == 0:
            print("✅ Status: CLEAN - No garbage detected!")
            status = "CLEAN"
            severity = "NONE"
        elif total <= 3:
            print(f"⚠️  Status: LOW - Found {total} waste item(s)")
            status = "LOW"
            severity = "MINOR"
        elif total <= 7:
            print(f"⚠️  Status: MODERATE - Found {total} waste item(s)")
            status = "MODERATE"
            severity = "MEDIUM"
        else:
            print(f"🚨 Status: HIGH - Found {total} waste item(s)")
            status = "HIGH"
            severity = "CRITICAL"
        
        print(f"\nTotal Waste Items: {total}")
        print(f"Severity Level: {severity}")
        print(f"Cleanliness Score: {max(0, 100 - (total * 10))}/100")
        
        if detection_data["class_counts"]:
            print("\n🗑️  Breakdown by Type:")
            for label, count in sorted(detection_data["class_counts"].items(), 
                                       key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                print(f"   • {label}: {count} items ({percentage:.1f}%)")
        
        # Detailed detections
        if detection_data["detections"]:
            print("\n📋 Detected Objects:")
            for i, det in enumerate(detection_data["detections"], 1):
                print(f"   {i}. {det['label']} - Confidence: {det['confidence']:.1%}")
        
        # Generate JSON report
        report_data = {
            "report_id": self.report_id,
            "timestamp": timestamp,
            "image": {
                "original": str(image_path),
                "before": str(before_path),
                "after": str(after_path),
                "size": detection_data["image_size"]
            },
            "detection": {
                "total_items": total,
                "status": status,
                "severity": severity,
                "cleanliness_score": max(0, 100 - (total * 10)),
                "confidence_threshold": self.confidence
            },
            "statistics": {
                "class_counts": detection_data["class_counts"],
                "detections": detection_data["detections"]
            },
            "model": {
                "path": str(self.model_path),
                "type": "YOLOv8"
            }
        }
        
        json_path = report_dir / f"report_{self.report_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate text report
        txt_path = report_dir / f"report_{self.report_id}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CLEANEYE - AI GARBAGE DETECTION REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Report ID: {self.report_id}\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Image: {image_path.name}\n\n")
            f.write("-" * 80 + "\n")
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Waste Detected: {total} items\n")
            f.write(f"Status: {status}\n")
            f.write(f"Severity: {severity}\n")
            f.write(f"Cleanliness Score: {max(0, 100 - (total * 10))}/100\n\n")
            
            if detection_data["class_counts"]:
                f.write("-" * 80 + "\n")
                f.write("BREAKDOWN BY TYPE\n")
                f.write("-" * 80 + "\n")
                for label, count in detection_data["class_counts"].items():
                    f.write(f"  {label}: {count}\n")
                f.write("\n")
            
            if detection_data["detections"]:
                f.write("-" * 80 + "\n")
                f.write("DETAILED DETECTIONS\n")
                f.write("-" * 80 + "\n")
                for i, det in enumerate(detection_data["detections"], 1):
                    f.write(f"{i}. {det['label']} ({det['confidence']:.1%})\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("For ADIPEC 2025 - CleanEye by AlBaraa\n")
            f.write("=" * 80 + "\n")
        
        print("\n" + "=" * 80)
        print("💾 REPORT FILES GENERATED")
        print("=" * 80)
        print(f"📁 Location: {report_dir}")
        print(f"   • before_{image_path.name}")
        print(f"   • after_{image_path.name}")
        print(f"   • report_{self.report_id}.json")
        print(f"   • report_{self.report_id}.txt")
        print("=" * 80)
        
        return self.report_id


def main():
    parser = argparse.ArgumentParser(
        description="CleanEye - Generate Before/After Detection Reports"
    )
    parser.add_argument(
        "image",
        type=str,
        help="Path to image file"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=str(DEFAULT_WEIGHTS),
        help="Path to model weights"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold"
    )
    
    args = parser.parse_args()
    
    # Convert to Path
    image_path = Path(args.image)
    if not image_path.is_absolute():
        # Try relative to media folder
        if not image_path.exists():
            image_path = MEDIA_DIR / args.image
    
    if not image_path.exists():
        print(f"[ERROR] Image not found: {args.image}")
        return
    
    # Create reporter
    reporter = DetectionReport(Path(args.model), args.conf)
    
    # Load model
    if not reporter.load_model():
        return
    
    # Generate report
    report_id = reporter.generate_report(image_path)
    
    print(f"\n✅ Report generated successfully!")
    print(f"📋 Report ID: {report_id}")
    print(f"\n💡 View your report in: outputs/reports/{report_id}/")


if __name__ == "__main__":
    main()
