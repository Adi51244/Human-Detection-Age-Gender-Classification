# 🌐 Human Detection Web App

A modern web application for real-time human detection and age/gender classification.

## 🚀 Quick Start

1. **Install Dependencies:**
```bash
pip install -r requirements_web.txt
```

2. **Start the Web App:**
```bash
python app.py
```

3. **Open Browser:**
Go to `http://localhost:5000`

## 🎯 Web Features

- **🔴 Live Detection:** Real-time camera streaming with detection
- **📤 Image Upload:** Upload images for analysis
- **📊 Statistics:** Real-time metrics and system info
- **📱 Responsive Design:** Works on desktop and mobile
- **🎨 Modern UI:** Beautiful gradient design with Bootstrap 5

## 🛠️ Web API Endpoints

- `GET /` - Main web interface
- `GET /api/cameras` - Get available cameras
- `POST /api/start_stream` - Start video stream
- `POST /api/stop_stream` - Stop video stream
- `GET /video_feed/<camera_id>` - Video streaming endpoint
- `GET /api/detections` - Get current detection results
- `POST /api/upload` - Upload image for analysis

## 🎨 Web Interface Features

### Live Detection Tab
- Camera selection dropdown
- Start/Stop controls
- Real-time video stream
- Live statistics (People count, FPS)
- Recent detections list

### Image Upload Tab
- Drag & drop image upload
- Click to select files
- Processed image display
- Detection results

### Statistics Tab
- Total detection count
- System accuracy (93%)
- Model information
- Device information

## 📱 Mobile Responsive

The web app is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🎯 Usage

1. **Live Detection:**
   - Select a camera from the dropdown
   - Click "Start Detection"
   - View real-time results

2. **Image Analysis:**
   - Go to "Image Upload" tab
   - Drag & drop or click to select image
   - View processed results

## 🔧 Configuration

The web app runs on:
- Host: `0.0.0.0` (all interfaces)
- Port: `5000`
- Debug: `True` (development mode)

## 🌟 Technical Stack

- **Backend:** Flask (Python)
- **Frontend:** Bootstrap 5, JavaScript
- **AI Models:** YOLOv8 + ResNet-18
- **Video:** OpenCV streaming
- **Icons:** Font Awesome 6

Enjoy your web-based human detection system! 🚀