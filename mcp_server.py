"""
CleanEye MCP Server
-------------------
Model Context Protocol server that exposes CleanEye's garbage detection
capabilities as tools for AI agents to use.

This allows LLMs and other agents to:
- Detect garbage in images/videos
- Get real-time detection statistics
- Access detection reports and logs
- Control detection parameters
"""

import asyncio
import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Import CleanEye detection functionality
import sys
sys.path.append(str(Path(__file__).parent / "code"))

from ultralytics import YOLO
import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent
MODEL_PATH = ROOT_DIR / "Weights" / "best.pt"
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOG_SUMMARY_PATH = OUTPUTS_DIR / "logs" / "live_summary.json"

# Initialize server
server = Server("cleaneye-mcp")

# Global model instance
_model = None


def get_model():
    """Lazy load the YOLO model"""
    global _model
    if _model is None:
        _model = YOLO(str(MODEL_PATH))
    return _model


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available CleanEye tools for AI agents.
    """
    return [
        types.Tool(
            name="detect_garbage_image",
            description=(
                "Detect garbage in an image. Provide either a file path or base64-encoded image. "
                "Returns detected objects with bounding boxes, confidence scores, and waste categories. "
                "Categories: 0, c, garbage, garbage_bag, waste, trash."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file (absolute or relative to CleanEye folder)"
                    },
                    "image_base64": {
                        "type": "string",
                        "description": "Base64-encoded image data (alternative to image_path)"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence threshold (0-1), default 0.25",
                        "default": 0.25
                    },
                    "iou": {
                        "type": "number",
                        "description": "IoU threshold for NMS (0-1), default 0.45",
                        "default": 0.45
                    }
                },
                "oneOf": [
                    {"required": ["image_path"]},
                    {"required": ["image_base64"]}
                ]
            },
        ),
        types.Tool(
            name="get_detection_statistics",
            description=(
                "Get real-time detection statistics from the live detection system. "
                "Returns total detections, breakdown by waste category, and recent activity."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="analyze_area_severity",
            description=(
                "Analyze the severity of garbage in an area based on detection results. "
                "Provide detection results and get a severity score (clean, moderate, severe) "
                "with recommendations for cleanup priority."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "detection_count": {
                        "type": "integer",
                        "description": "Number of garbage items detected"
                    },
                    "image_area": {
                        "type": "number",
                        "description": "Total image area in pixels (width * height)"
                    },
                    "detection_areas": {
                        "type": "array",
                        "description": "Array of bounding box areas for each detection",
                        "items": {"type": "number"}
                    }
                },
                "required": ["detection_count", "image_area"]
            },
        ),
        types.Tool(
            name="get_detection_reports",
            description=(
                "List all available detection reports. Returns metadata about saved reports "
                "including report IDs, timestamps, and detection counts."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of reports to return, default 10",
                        "default": 10
                    }
                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests from AI agents.
    """
    if name == "detect_garbage_image":
        return await detect_garbage_image(arguments or {})
    elif name == "get_detection_statistics":
        return await get_detection_statistics()
    elif name == "analyze_area_severity":
        return await analyze_area_severity(arguments or {})
    elif name == "get_detection_reports":
        return await get_detection_reports(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")


async def detect_garbage_image(args: Dict[str, Any]) -> list[types.TextContent]:
    """
    Detect garbage in an image using YOLOv8.
    """
    confidence = args.get("confidence", 0.25)
    iou = args.get("iou", 0.45)
    
    # Load image
    if "image_path" in args:
        img_path = Path(args["image_path"])
        if not img_path.is_absolute():
            img_path = ROOT_DIR / img_path
        
        if not img_path.exists():
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Image not found: {img_path}"})
            )]
        
        image = cv2.imread(str(img_path))
    
    elif "image_base64" in args:
        # Decode base64 image
        img_data = base64.b64decode(args["image_base64"])
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": "Either image_path or image_base64 must be provided"})
        )]
    
    if image is None:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": "Failed to load image"})
        )]
    
    # Run detection
    model = get_model()
    results = model.predict(
        image,
        conf=confidence,
        iou=iou,
        verbose=False
    )
    
    # Parse results
    detections = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]
            
            detections.append({
                "category": label,
                "confidence": round(conf, 3),
                "bounding_box": {
                    "x1": round(x1, 1),
                    "y1": round(y1, 1),
                    "x2": round(x2, 1),
                    "y2": round(y2, 1)
                },
                "area": round((x2 - x1) * (y2 - y1), 1)
            })
    
    # Generate summary
    h, w = image.shape[:2]
    category_counts = {}
    for det in detections:
        cat = det["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    result_data = {
        "total_detections": len(detections),
        "image_size": {"width": w, "height": h},
        "category_breakdown": category_counts,
        "detections": detections,
        "severity": _calculate_severity(len(detections), w * h, [d["area"] for d in detections])
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]


async def get_detection_statistics() -> list[types.TextContent]:
    """
    Get statistics from the live detection system.
    """
    if not LOG_SUMMARY_PATH.exists():
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "no_data",
                "message": "No live detection statistics available. Run the detection system first."
            })
        )]
    
    with open(LOG_SUMMARY_PATH, "r") as f:
        stats = json.load(f)
    
    return [types.TextContent(
        type="text",
        text=json.dumps(stats, indent=2)
    )]


async def analyze_area_severity(args: Dict[str, Any]) -> list[types.TextContent]:
    """
    Analyze the severity of garbage in an area.
    """
    detection_count = args.get("detection_count", 0)
    image_area = args.get("image_area", 1)
    detection_areas = args.get("detection_areas", [])
    
    severity = _calculate_severity(detection_count, image_area, detection_areas)
    
    # Generate recommendations
    if severity["level"] == "clean":
        recommendation = "Area appears clean. Regular monitoring recommended."
        priority = "low"
    elif severity["level"] == "moderate":
        recommendation = "Moderate waste detected. Schedule cleanup within 24-48 hours."
        priority = "medium"
    else:  # severe
        recommendation = "High waste concentration detected. Immediate cleanup required!"
        priority = "high"
    
    analysis = {
        "severity": severity,
        "cleanup_priority": priority,
        "recommendation": recommendation,
        "metrics": {
            "detection_count": detection_count,
            "density": severity["density"],
            "coverage": severity["coverage_percent"]
        }
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(analysis, indent=2)
    )]


async def get_detection_reports(args: Dict[str, Any]) -> list[types.TextContent]:
    """
    List available detection reports.
    """
    limit = args.get("limit", 10)
    reports_dir = OUTPUTS_DIR / "reports"
    
    if not reports_dir.exists():
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "no_reports",
                "message": "No detection reports available."
            })
        )]
    
    # List report directories
    report_folders = sorted(reports_dir.glob("CLN-*"), key=lambda p: p.stat().st_mtime, reverse=True)
    report_folders = report_folders[:limit]
    
    reports = []
    for folder in report_folders:
        report_id = folder.name
        # Try to read detection count from report files
        detection_count = 0
        report_files = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
        
        reports.append({
            "report_id": report_id,
            "timestamp": report_id.split("-")[1:3],  # Date and time
            "path": str(folder),
            "num_files": len(report_files)
        })
    
    return [types.TextContent(
        type="text",
        text=json.dumps({
            "total_reports": len(reports),
            "reports": reports
        }, indent=2)
    )]


def _calculate_severity(detection_count: int, image_area: float, detection_areas: List[float]) -> Dict[str, Any]:
    """
    Calculate severity based on detection metrics.
    """
    # Calculate density (detections per 1000 pixels)
    density = (detection_count / image_area) * 1000 if image_area > 0 else 0
    
    # Calculate coverage percentage
    total_detection_area = sum(detection_areas) if detection_areas else 0
    coverage_percent = (total_detection_area / image_area * 100) if image_area > 0 else 0
    
    # Determine severity level
    if detection_count == 0:
        level = "clean"
        score = 0
    elif detection_count < 3 or coverage_percent < 5:
        level = "clean"
        score = 1
    elif detection_count < 8 or coverage_percent < 15:
        level = "moderate"
        score = 2
    else:
        level = "severe"
        score = 3
    
    return {
        "level": level,
        "score": score,
        "density": round(density, 4),
        "coverage_percent": round(coverage_percent, 2),
        "detection_count": detection_count
    }


async def main():
    """
    Run the MCP server using stdin/stdout.
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cleaneye",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
