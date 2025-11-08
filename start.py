"""
CleanEye launcher.
Use this menu to start the Streamlit demo, run YOLO detectors, or access tools.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parent
CODE_DIR = ROOT_DIR / "code"
PYTHON = sys.executable


def get_local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "localhost"


def run_streamlit() -> None:
    ip = get_local_ip()
    print("\nLaunching Streamlit demo...")
    print("=" * 60)
    print("Share these URLs with visitors on the same network:")
    print(f"- Localhost : http://localhost:8501")
    print(f"- Network   : http://{ip}:8501")
    print("=" * 60)
    try:
        subprocess.run(
            [
                PYTHON,
                "-m",
                "streamlit",
                "run",
                str(CODE_DIR / "app.py"),
                "--server.address",
                "0.0.0.0",
                "--server.port",
                "8501",
            ],
            check=False,
        )
    except KeyboardInterrupt:
        print("\n[INFO] Streamlit stopped by user.")


def run_detector() -> None:
    cmd = [PYTHON, str(CODE_DIR / "detect_pro.py")]
    subprocess.run(cmd, check=False)


def run_image_tester() -> None:
    cmd = [PYTHON, str(CODE_DIR / "test_img.py")]
    subprocess.run(cmd, check=False)


def run_video_tester() -> None:
    cmd = [PYTHON, str(CODE_DIR / "test_vid.py")]
    subprocess.run(cmd, check=False)


def run_training() -> None:
    cmd = [PYTHON, str(CODE_DIR / "train.py")]
    subprocess.run(cmd, check=False)


def run_qr_generator() -> None:
    cmd = [PYTHON, str(CODE_DIR / "generate_qr.py")]
    subprocess.run(cmd, check=False)


def open_outputs() -> None:
    outputs_path = ROOT_DIR / "outputs"
    outputs_path.mkdir(exist_ok=True)
    if sys.platform == "win32":
        os.startfile(outputs_path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(outputs_path)], check=False)
    else:
        subprocess.run(["xdg-open", str(outputs_path)], check=False)


MENU: Dict[str, Tuple[str, Callable[[], None]]] = {
    "1": ("Launch Streamlit demo", run_streamlit),
    "2": ("Run live camera detector", run_detector),
    "3": ("Test sample images", run_image_tester),
    "4": ("Test video file", run_video_tester),
    "5": ("Train or resume model", run_training),
    "6": ("Generate QR code", run_qr_generator),
    "7": ("Open outputs folder", open_outputs),
    "q": ("Quit", lambda: None),
}


def print_menu() -> None:
    print("\n" + "=" * 60)
    print("CleanEye – ADIPEC 2025 Quick Launcher")
    print("=" * 60)
    for key, (label, _) in MENU.items():
        print(f"[{key}] {label}")
    print("=" * 60)


def main() -> None:
    while True:
        print_menu()
        choice = input("Select an option: ").strip().lower()
        if choice not in MENU:
            print("[WARN] Invalid selection. Try again.")
            continue
        if choice == "q":
            print("Goodbye!")
            break
        action = MENU[choice][1]
        action()


if __name__ == "__main__":
    main()
