# 🧠 Models Directory

This directory contains the AI models required for human detection and age/gender classification.

## 📋 Required Models

### 1. 🎯 YOLOv8 Detection Model
- **File**: `yolov8n.pt` (should be in parent directory)
- **Purpose**: Human/person detection
- **Size**: ~6MB
- **Download**: Automatically downloaded by ultralytics on first run
- **Command**: `from ultralytics import YOLO; model = YOLO('yolov8n.pt')`

### 2. 🧠 ResNet-18 Age/Gender Classification Model
- **File**: `ResNet-18 Age 0.60 + Gender 93 (1).pt`
- **Purpose**: Age group and gender classification
- **Accuracy**: 93% gender classification
- **Size**: ~44MB
- **Note**: This is a custom trained model

## 🚀 Model Setup

1. **YOLOv8 Model**: Will be auto-downloaded on first run
2. **ResNet-18 Model**: Place the `.pt` file in this directory

## 📁 Directory Structure

```
models/
├── README.md                                    # This file
└── ResNet-18 Age 0.60 + Gender 93 (1).pt      # Age/Gender model (required)
```

## ⚠️ Important Notes

- Model files are excluded from git tracking due to size limitations
- YOLOv8 model (`yolov8n.pt`) should be in the parent directory
- Ensure you have the ResNet-18 model file for age/gender classification
- All models are loaded automatically by the main script

## 🔧 Troubleshooting

If you encounter model loading errors:
1. Check if the model files exist in the correct locations
2. Verify PyTorch and Ultralytics are properly installed
3. Ensure model file names match exactly as expected in the code
