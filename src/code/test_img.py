"""
CleanEye image tester.
Detect litter on individual images for quick validation or demos.
"""

from __future__ import annotations

import argparse
import cv2
from pathlib import Path
from typing import Dict

from ultralytics import YOLO

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = ROOT_DIR / "Weights" / "best.pt"
MEDIA_DIR = ROOT_DIR / "media"
OUTPUT_DIR = ROOT_DIR / "outputs"

# Simple color mapping - use raw model labels directly
COLORS = {
    "0": (0, 165, 255),           # Orange
    "c": (255, 215, 0),            # Gold
    "garbage": (0, 0, 255),        # Red
    "garbage_bag": (255, 0, 255),  # Magenta
    "waste": (0, 255, 0),          # Green
    "trash": (255, 140, 0),        # Dark Orange
}


def load_model(weights: Path) -> YOLO:
    print(f"[INFO] Loading model from {weights} ...")
    model = YOLO(str(weights))
    print("[INFO] Model ready.")
    return model


def annotate(model: YOLO, image_path: Path, confidence: float) -> int:
    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"Unable to open image: {image_path}")

    results = model(image, conf=confidence, verbose=False)
    boxes = results[0].boxes
    detections = 0

    for box in boxes:
        cls_id = int(box.cls[0])
        raw_label = model.names[cls_id]
        color = COLORS.get(raw_label, (255, 255, 255))
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            image,
            f"{raw_label} {conf:.0%}",
            (x1, max(25, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA,
        )
        detections += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"detection_{image_path.name}"
    cv2.imwrite(str(output_path), image)
    print(f"[INFO] Saved annotated image to {output_path}")

    cv2.imshow("CleanEye Image Tester", image)
    print("[INFO] Press 'q' to close the preview window.")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    return detections


def list_media_images() -> list[Path]:
    if not MEDIA_DIR.exists():
        return []
    return sorted([path for path in MEDIA_DIR.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"}])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run CleanEye on image files.")
    parser.add_argument("images", nargs="*", type=Path, help="Image paths. If empty, media folder will be listed.")
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS, help="Path to YOLO weights.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold (lower = more detections).")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    selection = args.images or list_media_images()
    if not selection:
        raise SystemExit("[WARN] No images specified and media folder is empty.")

    model = load_model(args.weights)

    for image_path in selection:
        if not image_path.exists():
            print(f"[WARN] Skipping missing image: {image_path}")
            continue
        print(f"[INFO] Processing {image_path.name} ...")
        detections = annotate(model, image_path, args.conf)
        print(f"[INFO] Found {detections} detection(s).")


if __name__ == "__main__":
    main()
