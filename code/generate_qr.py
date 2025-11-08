"""
Generate a QR code that points to the local CleanEye Streamlit app.
Adds the URL text below the code for easy identification.
"""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Optional

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - handled at runtime
    qrcode = None
    Image = None
    ImageDraw = None
    ImageFont = None

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT_DIR / "cleaneye_qr.png"


def get_local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "127.0.0.1"


def build_qr_image(url: str) -> Optional["Image.Image"]:
    if qrcode is None or Image is None or ImageDraw is None or ImageFont is None:
        return None

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Add label beneath the code
    font = ImageFont.load_default()
    dummy = Image.new("RGB", (1, 1), "white")
    draw = ImageDraw.Draw(dummy)
    text_bbox = draw.textbbox((0, 0), url, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    padding = 20

    canvas_width = max(qr_img.width, text_width + padding)
    canvas_height = qr_img.height + text_height + padding * 2
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    canvas.paste(qr_img, ((canvas_width - qr_img.width) // 2, padding))

    canvas_draw = ImageDraw.Draw(canvas)
    text_position = ((canvas_width - text_width) // 2, qr_img.height + padding)
    canvas_draw.text(text_position, url, fill="black", font=font)
    return canvas


def main() -> None:
    if qrcode is None:
        raise SystemExit("Install the qrcode and pillow packages to generate QR codes (`pip install qrcode[pil]`).")

    ip = get_local_ip()
    url = f"http://{ip}:8501"

    print("=" * 50)
    print("CleanEye QR Code Generator")
    print("=" * 50)
    print(f"Detected IP address: {ip}")
    print(f"Streamlit URL     : {url}")

    image = build_qr_image(url)
    if image is None:
        raise SystemExit("Pillow is required to draw the QR code label (`pip install pillow`).")

    image.save(OUTPUT_FILE)
    print(f"[INFO] QR code saved to {OUTPUT_FILE}")
    print("[TIP] Print the image and place it at the booth for instant access.")


if __name__ == "__main__":
    main()
