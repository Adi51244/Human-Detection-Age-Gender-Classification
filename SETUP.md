# 🚀 Quick Setup Guide

## 📦 One-Line Installation

```bash
git clone https://github.com/Adi51244/human_detection.git
cd human_detection
pip install -r requirements.txt
python yolo_webcam.py
```

## 🧠 Model Setup

The YOLOv8 model will be automatically downloaded on first run.

**Important**: You need to place the ResNet-18 age/gender classification model in the `models/` directory:
- File: `ResNet-18 Age 0.60 + Gender 93 (1).pt`
- This model provides 93% gender classification accuracy

## 🎮 Usage

1. Run: `python yolo_webcam.py`
2. Select camera (0, 1, 2...)
3. Position yourself in front of camera
4. See real-time detection and classification!
5. Press `q` to quit

## 🔧 Requirements

- Python 3.8+
- Webcam
- ~500MB disk space

That's it! 🎉
