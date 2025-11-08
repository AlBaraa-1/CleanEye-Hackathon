"""
CleanEye - Professional Garbage Detection (CLI)
------------------------------------------------
Runs YOLOv8 inference on webcam, image, or video sources and logs
results for the Streamlit dashboard.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from random import uniform
from typing import Deque, Dict, Optional, Tuple

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except ImportError as exc:  # pragma: no cover - handled by CLI
    print("Ultralytics is required. Install with `pip install ultralytics`.", file=sys.stderr)
    raise SystemExit(1) from exc


ROOT_DIR = Path(__file__).resolve().parent.parent  # CleanEye directory (go up from code/)
MODEL_PATH = ROOT_DIR / "Weights" / "best.pt"
OUTPUT_DIR = ROOT_DIR / "outputs"
LOG_DIR = OUTPUT_DIR / "logs"
SNAPSHOT_DIR = OUTPUT_DIR / "snapshots"
AUTO_SAVE_DIR = OUTPUT_DIR / "auto_saves"
LOG_FILE = LOG_DIR / "live_detections.jsonl"
SUMMARY_FILE = LOG_DIR / "live_summary.json"
BOOTH_COORDINATES = (24.4181, 54.4583)  # ADIPEC venue (approximate latitude, longitude)

# Simple color mapping - use raw model labels directly
COLORS = {
    "0": (0, 165, 255),           # Orange
    "c": (255, 215, 0),            # Gold
    "garbage": (0, 0, 255),        # Red
    "garbage_bag": (255, 0, 255),  # Magenta
    "waste": (0, 255, 0),          # Green
    "trash": (255, 140, 0),        # Dark Orange
}

# Category mapping for statistics only
CATEGORIES = {
    "0": "General",
    "c": "Recyclable",
    "garbage": "General",
    "garbage_bag": "Recyclable",
    "waste": "General",
    "trash": "General",
}


def ensure_directories() -> None:
    """Create required output folders."""
    for path in (OUTPUT_DIR, LOG_DIR, SNAPSHOT_DIR, AUTO_SAVE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def check_environment() -> bool:
    """Confirm required assets are available before running detection."""
    ensure_directories()
    ok = True

    if not MODEL_PATH.exists():
        print(f"[ERROR] Model weights not found at {MODEL_PATH}")
        ok = False
    else:
        print(f"[OK] Using weights at {MODEL_PATH}")

    return ok


@dataclass
class DetectionEvent:
    timestamp: str
    source: str
    frame_index: int
    raw_label: str
    friendly_label: str
    category: str
    confidence: float
    latitude: float
    longitude: float


class DetectionLogger:
    """Persist detection events and maintain live summaries for the dashboard."""

    def __init__(self, logfile: Path = LOG_FILE, summary_file: Path = SUMMARY_FILE) -> None:
        self.logfile = logfile
        self.summary_file = summary_file
        self.class_counts: Dict[str, int] = defaultdict(int)
        self.category_counts: Dict[str, int] = defaultdict(int)
        self.total_events = 0
        self.last_event: Optional[DetectionEvent] = None
        ensure_directories()

    def record(self, event: DetectionEvent) -> None:
        self.total_events += 1
        self.class_counts[event.friendly_label] += 1
        self.category_counts[event.category] += 1
        self.last_event = event

        with self.logfile.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.__dict__) + "\n")

        summary = {
            "updated_at": event.timestamp,
            "total_detections": self.total_events,
            "class_counts": dict(self.class_counts),
            "category_counts": dict(self.category_counts),
            "last_event": event.__dict__,
            "location_hint": {"latitude": event.latitude, "longitude": event.longitude},
        }

        with self.summary_file.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)


class GarbageDetector:
    """YOLOv8 based detector with logging and statistics."""

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        confidence: float = 0.25,  # Lower default for better detection
        auto_save: bool = False,
        logger: Optional[DetectionLogger] = None,
    ) -> None:
        self.model_path = model_path
        self.confidence = confidence
        self.auto_save = auto_save
        self.logger = logger or DetectionLogger()
        self.model: Optional[YOLO] = None
        self.frame_history: Deque[float] = deque(maxlen=120)
        self.total_frames = 0
        self.total_detections = 0

    def load_model(self) -> bool:
        """Load YOLO model from disk."""
        try:
            self.model = YOLO(str(self.model_path))
            print("[OK] Model loaded.")
            return True
        except Exception as exc:  # pragma: no cover - runtime guard
            print(f"[ERROR] Failed to load model: {exc}")
            return False

    def _annotate_frame(self, frame: np.ndarray, result, source: str) -> Tuple[np.ndarray, int]:
        annotated = frame.copy()
        detections = 0

        for box in result.boxes:
            detections += 1
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            raw_label = self.model.names[cls_id] if self.model else str(cls_id)
            color = COLORS.get(raw_label, (255, 255, 255))
            category = CATEGORIES.get(raw_label, "Unknown")

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            label_text = f"{raw_label} {conf:.0%}"
            cv2.putText(
                annotated,
                label_text,
                (x1, max(25, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
                cv2.LINE_AA,
            )

            latitude = BOOTH_COORDINATES[0] + uniform(-0.0008, 0.0008)
            longitude = BOOTH_COORDINATES[1] + uniform(-0.0008, 0.0008)

            event = DetectionEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                source=source,
                frame_index=self.total_frames,
                raw_label=raw_label,
                friendly_label=raw_label,
                category=category,
                confidence=conf,
                latitude=latitude,
                longitude=longitude,
            )
            self.logger.record(event)

        return annotated, detections

    def run_webcam(self, source: int) -> None:
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"[ERROR] Unable to open camera index {source}.")
            return

        start_time = time.time()
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    print("[WARN] Unable to read frame from camera.")
                    break

                self.total_frames += 1
                inference_start = time.time()
                results = self.model(frame, conf=self.confidence, verbose=False)
                inference_ms = (time.time() - inference_start) * 1000
                annotated, detected = self._annotate_frame(frame, results[0], source=f"camera:{source}")
                self.total_detections += detected

                if self.auto_save and detected > 0:
                    filename = AUTO_SAVE_DIR / f"detection_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                    cv2.imwrite(str(filename), frame)

                elapsed = time.time() - start_time
                fps = self.total_frames / elapsed if elapsed > 0 else 0.0
                self.frame_history.append(fps)

                overlay = f"Frames: {self.total_frames} | Detections: {self.total_detections} | Inference: {inference_ms:.1f} ms | FPS: {fps:.1f}"
                cv2.putText(
                    annotated,
                    overlay,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow("CleanEye - Live Detection", annotated)
                key = cv2.waitKey(1) & 0xFF

                if key in (ord("q"), ord("Q")):
                    print("[INFO] Stopping detection.")
                    break
                if key in (ord("s"), ord("S")):
                    filename = SNAPSHOT_DIR / f"snapshot_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(str(filename), annotated)
                    print(f"[OK] Snapshot saved to {filename}")
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def run_image(self, image_path: Path) -> None:
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        if not image_path.exists():
            print(f"[ERROR] Image not found: {image_path}")
            return

        image = cv2.imread(str(image_path))
        results = self.model(image, conf=self.confidence, verbose=False)
        self.total_frames += 1
        annotated, detected = self._annotate_frame(image, results[0], source=str(image_path))
        self.total_detections += detected
        output_file = OUTPUT_DIR / f"image_detection_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(str(output_file), annotated)
        print(f"[OK] Processed image. Detections: {detected}. Saved to {output_file}")

    def run_video(self, video_path: Path) -> None:
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        if not video_path.exists():
            print(f"[ERROR] Video not found: {video_path}")
            return

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"[ERROR] Unable to open video: {video_path}")
            return

        try:
            while True:
                success, frame = cap.read()
                if not success:
                    print("[INFO] Video ended.")
                    break

                self.total_frames += 1
                results = self.model(frame, conf=self.confidence, verbose=False)
                annotated, detected = self._annotate_frame(frame, results[0], source=str(video_path))
                self.total_detections += detected
                cv2.imshow("CleanEye - Video Detection", annotated)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), ord("Q")):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CleanEye - Garbage Detection",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("mode", choices=["webcam", "image", "video"], nargs="?", default="webcam", help="Detection mode")
    parser.add_argument("input", nargs="?", help="Image or video path when using the respective mode")
    parser.add_argument("--model", default=str(MODEL_PATH), help="Path to YOLO weights")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold (default: 0.25 for better detection)")
    parser.add_argument("--source", type=int, default=0, help="Camera index when using webcam mode")
    parser.add_argument("--auto-save", action="store_true", help="Automatically save frames that contain detections")
    return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> None:
    args = parse_args(argv)
    if not check_environment():
        raise SystemExit(1)

    detector = GarbageDetector(
        model_path=Path(args.model),
        confidence=args.conf,
        auto_save=args.auto_save,
    )

    if not detector.load_model():
        raise SystemExit(1)

    if args.mode == "webcam":
        detector.run_webcam(args.source)
    elif args.mode == "image":
        if not args.input:
            print("[ERROR] Please provide an image path.")
            raise SystemExit(1)
        detector.run_image(Path(args.input))
    elif args.mode == "video":
        if not args.input:
            print("[ERROR] Please provide a video path.")
            raise SystemExit(1)
        detector.run_video(Path(args.input))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
