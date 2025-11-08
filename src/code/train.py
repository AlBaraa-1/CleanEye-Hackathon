"""
CleanEye training script.
Wraps ultralytics YOLO training with sensible defaults and logging.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import torch
from ultralytics import YOLO

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_CONFIG = ROOT_DIR / "data" / "data.yaml"
OUTPUT_DIR = ROOT_DIR / "outputs"
TRAIN_LOG = OUTPUT_DIR / "logs" / "latest_training.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train CleanEye YOLO model.")
    parser.add_argument("--data", type=Path, default=DATA_CONFIG, help="Path to data.yaml configuration.")
    parser.add_argument("--epochs", type=int, default=80, help="Number of training epochs.")
    parser.add_argument("--batch", type=int, default=16, help="Batch size.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size.")
    parser.add_argument("--weights", type=str, default="yolov8s.pt", help="Base model weights to fine tune.")
    parser.add_argument("--project", type=Path, default=ROOT_DIR / "runs" / "detect", help="Training output directory.")
    parser.add_argument("--name", type=str, default="cleaneye_train", help="Run name inside the project directory.")
    parser.add_argument("--device", type=str, default=None, help="Torch device override (e.g. 'cpu', '0').")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience.")
    parser.add_argument("--freeze", type=int, default=0, help="Number of layers to freeze from the backbone.")
    parser.add_argument("--lr0", type=float, default=0.001, help="Initial learning rate.")
    parser.add_argument("--lrf", type=float, default=0.01, help="Final learning rate multiplier.")
    return parser.parse_args(argv)


def resolve_device(device_arg: str | None) -> str:
    if device_arg:
        return device_arg
    if torch.cuda.is_available():
        return "0"
    print("[WARN] CUDA not available; falling back to CPU. Training will be slower.")
    return "cpu"


def train_model(args: argparse.Namespace) -> Dict[str, Any]:
    device = resolve_device(args.device)
    print("=" * 60)
    print("CleanEye Training")
    print("=" * 60)
    print(f"Data config : {args.data}")
    print(f"Base weights: {args.weights}")
    print(f"Device      : {device}")
    print(f"Epochs      : {args.epochs}")
    print(f"Batch size  : {args.batch}")
    print(f"Image size  : {args.imgsz}")
    print("=" * 60)

    model = YOLO(args.weights)

    results = model.train(
        data=str(args.data),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        patience=args.patience,
        lr0=args.lr0,
        lrf=args.lrf,
        optimizer="AdamW",
        weight_decay=0.0005,
        project=str(args.project),
        name=args.name,
        exist_ok=True,
        device=device,
        freeze=args.freeze,
        verbose=True,
    )

    summary = {
        "run_completed": datetime.utcnow().isoformat(),
        "save_dir": str(results.save_dir),
        "epochs": args.epochs,
        "batch": args.batch,
        "image_size": args.imgsz,
        "device": device,
        "best_model": str(Path(results.save_dir) / "weights" / "best.pt"),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with TRAIN_LOG.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(f"[INFO] Training summary saved to {TRAIN_LOG}")
    return summary


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    train_model(args)


if __name__ == "__main__":
    main()
