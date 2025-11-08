"""
Quick verification script for CleanEye MCP Hackathon readiness
"""

import sys
from pathlib import Path

print("=" * 70)
print("  CleanEye - Hackathon Readiness Check")
print("=" * 70)
print()

# Check Python version
print("1. Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor} (OK)")
else:
    print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (Need 3.8+)")

print()

# Check required packages
print("2. Checking required packages...")
required_packages = [
    "ultralytics",
    "cv2",
    "streamlit",
    "numpy",
    "torch",
    "mcp"
]

for package in required_packages:
    try:
        if package == "cv2":
            import cv2
            print(f"   ✅ opencv-python (cv2)")
        else:
            __import__(package)
            print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} (NOT INSTALLED - run: pip install {package})")

print()

# Check project structure
print("3. Checking project structure...")
root = Path(__file__).parent
required_files = [
    "mcp_server.py",
    "mcp_demo.py",
    "MCP_README.md",
    "HACKATHON_SUBMISSION.md",
    "requirements.txt",
    "code/app.py",
    "Weights/best.pt"
]

for file in required_files:
    file_path = root / file
    if file_path.exists():
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} (MISSING)")

print()

# Check model weights
print("4. Checking model weights...")
weights_path = root / "Weights" / "best.pt"
if weights_path.exists():
    size_mb = weights_path.stat().st_size / (1024 * 1024)
    print(f"   ✅ Model found ({size_mb:.1f} MB)")
    
    # Try to load model
    try:
        from ultralytics import YOLO
        model = YOLO(str(weights_path))
        print(f"   ✅ Model loads successfully")
        print(f"   ℹ️  Classes: {list(model.names.values())}")
    except Exception as e:
        print(f"   ⚠️  Model file exists but couldn't load: {e}")
else:
    print(f"   ❌ Model not found at {weights_path}")

print()

# Check outputs directory
print("5. Checking outputs directory...")
outputs_dir = root / "outputs"
if outputs_dir.exists():
    print(f"   ✅ outputs/ directory exists")
    
    # Check subdirectories
    subdirs = ["logs", "reports", "snapshots", "auto_saves"]
    for subdir in subdirs:
        subdir_path = outputs_dir / subdir
        if not subdir_path.exists():
            print(f"   ℹ️  Creating {subdir}/ directory...")
            subdir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created {subdir}/")
else:
    print(f"   ⚠️  outputs/ directory not found, creating...")
    outputs_dir.mkdir(exist_ok=True)
    for subdir in ["logs", "reports", "snapshots", "auto_saves"]:
        (outputs_dir / subdir).mkdir(exist_ok=True)
    print(f"   ✅ Created outputs/ structure")

print()

# Check media directory
print("6. Checking test media...")
media_dir = root / "media"
if media_dir.exists():
    images = list(media_dir.glob("*.jpg")) + list(media_dir.glob("*.png"))
    videos = list(media_dir.glob("*.mp4")) + list(media_dir.glob("*.avi"))
    
    print(f"   ✅ media/ directory exists")
    print(f"   ℹ️  {len(images)} test images found")
    print(f"   ℹ️  {len(videos)} test videos found")
    
    if len(images) == 0:
        print(f"   ⚠️  No test images found - add some for demo!")
else:
    print(f"   ⚠️  media/ directory not found")
    print(f"   ℹ️  Create it and add test images for demo")

print()

# Test MCP import
print("7. Testing MCP functionality...")
try:
    import mcp
    import mcp.server.stdio
    import mcp.types
    from mcp.server import Server
    print(f"   ✅ MCP imports successful")
    print(f"   ℹ️  MCP version: {getattr(mcp, '__version__', 'unknown')}")
except ImportError as e:
    print(f"   ❌ MCP import failed: {e}")
    print(f"   ℹ️  Install with: pip install mcp")

print()

# Summary
print("=" * 70)
print("  Summary")
print("=" * 70)
print()
print("If all checks passed ✅, you're ready for the hackathon!")
print()
print("Next steps:")
print("  1. Run: python mcp_demo.py")
print("  2. Test: streamlit run code/app.py")
print("  3. Read: HACKATHON_SETUP.md for detailed checklist")
print()
print("Join Discord: https://discord.gg/92sEPT2Zhv")
print("Channel: mcp-1st-birthday-official🏆")
print()
print("=" * 70)
