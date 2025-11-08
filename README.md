# 🗑️ CleanEye - AI Garbage Detection System

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)
![MCP](https://img.shields.io/badge/MCP-Enabled-blueviolet.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**CleanEye** is an AI-powered garbage detection system built for ADIPEC 2025 and MCP 1st Birthday Hackathon. Using YOLOv8, it identifies and tracks waste in real-time through images, videos, and live webcam feeds. Now **MCP-enabled** for AI agent interaction!

> 🏆 **Built for MCP 1st Birthday Hackathon** - Track 2: MCP in Action (Agents)

---

## 🎯 Features

- 🤖 **AI Detection** - YOLOv8-based waste identification
- 📸 **Multi-Source** - Images, videos, and webcam support
- 🌐 **Web Dashboard** - Beautiful Streamlit interface
- 📊 **Analytics** - Real-time statistics and reports
- 📍 **Location Tracking** - GPS-tagged detections
- 📋 **Before/After Reports** - Comprehensive detection summaries
- 🎨 **Color-Coded** - Visual classification by waste type
- 🔌 **MCP Integration** - Expose tools for AI agents ([See MCP_README.md](MCP_README.md))

---

## 🗂️ Waste Categories

CleanEye detects **6 types** of waste:
- `0` - General waste
- `c` - Containers
- `garbage` - General garbage
- `garbage_bag` - Plastic bags
- `waste` - Waste items
- `trash` - Trash

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/AlBaraa-1/Computer-vision.git
cd Computer-vision/CleanEye

# Install dependencies
pip install -r requirements.txt

# Download model weights (if not included)
# Place best.pt in Weights/ folder
```

### Running the App

```bash
# Interactive launcher
python start.py

# Or directly run Streamlit dashboard
streamlit run code/app.py

# Or CLI detection
python code/detect_pro.py image media/test.jpg
```

---

## 📁 Project Structure

```
CleanEye/
├── code/                      # Application scripts
│   ├── app.py                # Streamlit web dashboard
│   ├── detect_pro.py         # CLI detection tool
│   ├── detect_report.py      # Before/after reports
│   ├── test_img.py           # Image tester
│   ├── test_vid.py           # Video tester
│   ├── train.py              # Model training
│   └── generate_qr.py        # QR code generator
├── Weights/
│   └── best.pt               # Trained YOLOv8 model
├── data/
│   └── data.yaml             # Dataset configuration
├── media/                     # Test images/videos
├── outputs/                   # Detection results
│   ├── logs/                 # JSON logs
│   ├── reports/              # Detection reports
│   └── snapshots/            # Saved frames
├── start.py                   # Main launcher
└── requirements.txt           # Python dependencies
```

---

## 💻 Usage Examples

### 1. Web Dashboard

```bash
streamlit run code/app.py
```

Open browser at `http://localhost:8501`

**Features:**
- Upload images or videos
- Adjust detection sensitivity
- View live statistics
- Interactive map
- Voice alerts (optional)

### 2. Command-Line Detection

**Image:**
```bash
python code/detect_pro.py image media/garbage.jpg
```

**Video:**
```bash
python code/detect_pro.py video media/garbage.mp4
```

**Webcam:**
```bash
python code/detect_pro.py webcam
```

### 3. Generate Reports

```bash
python code/detect_report.py media/garbage.jpg
```

Creates:
- Before/after images
- JSON report with statistics
- Unique report ID
- Cleanliness score

### 4. Test Scripts

**Quick image test:**
```bash
python code/test_img.py media/test.jpg
```

**Video player with controls:**
```bash
python code/test_vid.py
```

---

## 🔧 Configuration

### Model Settings

Confidence threshold (default: 0.25):
```python
# Lower = more detections (may include false positives)
# Higher = only confident detections

python code/detect_pro.py image test.jpg --conf 0.3
```

### Web Dashboard

In `code/app.py`:
- Adjust confidence slider (0.1 - 0.9)
- Enable/disable voice alerts
- Set video frame sampling rate

---

## 📊 Detection Reports

Generate comprehensive before/after reports:

```bash
python code/detect_report.py media/garbage_5.jpg
```

**Report includes:**
- Unique ID: `CLN-20251104-120709-231499D4`
- Status: CLEAN / LOW / MODERATE / HIGH
- Cleanliness score: 0-100
- Breakdown by waste type
- Before/after images

**Status Levels:**
| Items | Status | Score |
|-------|--------|-------|
| 0 | ✅ CLEAN | 100 |
| 1-3 | ⚠️ LOW | 70-90 |
| 4-7 | ⚠️ MODERATE | 30-60 |
| 8+ | 🚨 HIGH | 0-20 |

---

## 🌐 For ADIPEC Demo

### Setup Checklist

1. **Connect to venue WiFi**
2. **Generate QR code:**
   ```bash
   python code/generate_qr.py
   ```
3. **Print QR code** (`cleaneye_qr.png`)
4. **Start dashboard:**
   ```bash
   python start.py  # Choose option 1
   ```
5. **Visitors scan QR** → Access app on their phones

---

## 📱 QR Code Access

The QR code generator creates a scannable link to the web dashboard:

```bash
python code/generate_qr.py
```

Visitors can:
- Scan QR with their phones
- Upload images instantly
- See AI detections in real-time
- All on the same network!

---

## 🎓 Training Your Own Model

```bash
python code/train.py
```

**Requirements:**
- Dataset in `data/` folder
- YAML config: `data/data.yaml`
- GPU recommended (CUDA support)

**Training produces:**
- `runs/detect/*/weights/best.pt` - Best model
- Training metrics and graphs
- Validation results

---

## 🛠️ Technologies Used

- **YOLOv8** - Object detection (Ultralytics)
- **Python 3.12** - Programming language
- **Streamlit** - Web dashboard framework
- **OpenCV** - Computer vision library
- **Folium** - Interactive maps
- **Geopy** - Geographic calculations
- **PyTorch** - Deep learning backend

---

## 📋 Requirements

```txt
ultralytics>=8.0.0
opencv-python>=4.8.0
streamlit>=1.28.0
folium>=0.14.0
geopy>=2.4.0
pandas>=2.0.0
numpy>=1.24.0
pillow>=10.0.0
qrcode[pil]>=7.4.0
pyttsx3>=2.90  # Optional: voice alerts
```

---

## 🖥️ Hardware Requirements

**Minimum:**
- CPU: Intel i5 / AMD Ryzen 5
- RAM: 8GB
- Storage: 2GB free space

**Recommended:**
- CPU: Intel i7 / AMD Ryzen 7
- RAM: 16GB
- GPU: NVIDIA RTX 4060 or better (CUDA support)
- Storage: 5GB free space

**Tested on:**
- Desktop: NVIDIA RTX 4070 Ti SUPER
- Laptop: RTX 4060 (recommended for demos)

---

## 🎯 Performance

**Expected inference times:**
- **Image**: 50-100ms
- **Video**: 25-60 FPS real-time
- **Webcam**: 30-40 FPS smooth playback

**On RTX 4060 Laptop:**
- ✅ Real-time detection
- ✅ Multiple simultaneous users
- ✅ No lag or stuttering

---

## 📸 Screenshots

*Coming soon - Add screenshots of:*
- Web dashboard
- Detection results
- Before/after reports
- QR code interface

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**AlBaraa**
- GitHub: [@AlBaraa-1](https://github.com/AlBaraa-1)
- Project: Computer-vision/CleanEye

---

## 🏆 ADIPEC 2025

Built for the **ADIPEC 2025** technology showcase in Abu Dhabi, UAE.

**Mission:** Making cities cleaner through AI-powered waste detection and monitoring.

---

## 🙏 Acknowledgments

- **Ultralytics** - YOLOv8 framework
- **Roboflow** - Dataset tools
- **Streamlit** - Dashboard framework

---

## 📧 Contact

For questions or support:
- Open an issue on GitHub
- Email: [Your email if you want to add]

---

**⭐ If you find this project useful, please give it a star!**

---

*Built with ❤️ for a cleaner future 🌍♻️*
