from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
import torch
import os
import base64
from io import BytesIO
from PIL import Image
import json
import threading
import time

# Import your existing models
from ultralytics import YOLO
import torchvision.models as models
import torch.nn as nn
from torchvision.models import ResNet18_Weights

app = Flask(__name__)

# Global variables for camera and models
camera = None
is_streaming = False
detection_results = []
fps_counter = 0
start_time = time.time()

class HumanDetectionSystem:
    def __init__(self):
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.groups = ['00-10', '11-20', '21-30', '31-40', '41-50', 
                      '51-60', '61-70', '71-80', '81-90']
        self.face_detector = YOLO('yolov8n.pt')
        self.load_age_gender_model()
        
    def load_age_gender_model(self):
        """Load ResNet-18 model for age/gender classification."""
        age_model_path = os.path.abspath('models/ResNet-18 Age 0.60 + Gender 93 (1).pt')
        
        if not os.path.exists(age_model_path):
            raise FileNotFoundError(f"Model file not found: {age_model_path}")
        
        Classes = 9
        device = self.device
        
        resnet_base = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        resnet_base.fc = nn.Linear(512, Classes+2)
        self.resnet_model = nn.Sequential(resnet_base)
        self.resnet_model.load_state_dict(torch.load(age_model_path, map_location=device))
        self.resnet_model.eval()
        self.resnet_model.to(device)
        
    def classify_age_gender(self, face_img):
        """Classify age and gender using ResNet-18 model with performance optimization."""
        try:
            # Optimized preprocessing
            img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img_rgb, (200, 200), interpolation=cv2.INTER_LINEAR)
            
            # Fast tensor conversion
            img_tensor = torch.from_numpy(img).float().permute(2, 0, 1) / 255.0
            img_batch = img_tensor.unsqueeze(0).to(self.device, non_blocking=True)

            with torch.no_grad():
                logits = self.resnet_model(img_batch)[0]
                age_idx = torch.argmax(logits[:9]).item()
                gender_idx = torch.argmax(logits[9:]).item()
                
                age_label = self.groups[age_idx] if 0 <= age_idx < 9 else "Unknown"
                gender = 'Male' if gender_idx == 0 else 'Female'

            return gender, age_label
        except Exception as e:
            print(f"Error in classification: {e}")
            return "Unknown", "Unknown"
    
    def process_frame(self, frame):
        """Process frame for human detection and classification with performance optimization."""
        # Use smaller input size for YOLO for faster processing
        results = self.face_detector(frame, imgsz=640, conf=0.25, iou=0.4, verbose=False)
        boxes = results[0].boxes.data.cpu().numpy()
        
        detections = []
        annotated_frame = frame.copy()
        
        for box in boxes:
            x1, y1, x2, y2, score, cls = box
            if score < 0.25 or int(cls) != 0:  # Slightly lower threshold for more detections
                continue
                
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            
            # Draw bounding box with optimized drawing
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Extract and classify face
            face_img = frame[y1:y2, x1:x2]
            if face_img.size > 0:
                gender, age = self.classify_age_gender(face_img)
                
                # Optimized text rendering
                self.draw_text_with_background(annotated_frame, f'Age: {age}', 
                                             (x2 + 10, y1 + 20))
                self.draw_text_with_background(annotated_frame, f'Gender: {gender}', 
                                             (x2 + 10, y1 + 50))
                
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(score),
                    'age': age,
                    'gender': gender
                })
        
        return annotated_frame, detections
    
    def draw_text_with_background(self, frame, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, 
                                font_scale=0.7, color=(0, 255, 0), thickness=2, 
                                bg_color=(0, 0, 0), bg_padding=5):
        """Draw text with background."""
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        top_left = (position[0] - bg_padding, position[1] - text_height - bg_padding)
        bottom_right = (position[0] + text_width + bg_padding, position[1] + baseline + bg_padding)
        cv2.rectangle(frame, top_left, bottom_right, bg_color, cv2.FILLED)
        cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

# Initialize the detection system
detection_system = HumanDetectionSystem()

def generate_frames():
    """Generate video frames for streaming with high FPS optimization."""
    global camera, is_streaming, detection_results, fps_counter, start_time
    
    camera = cv2.VideoCapture(0)  # Always use default camera
    
    # High FPS optimizations
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 30)  # Set to 30 FPS
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
    
    is_streaming = True
    frame_count = 0
    fps_counter = 0
    start_time = time.time()
    
    while is_streaming:
        success, frame = camera.read()
        if not success:
            break
        
        frame_count += 1
        fps_counter += 1
        
        # Calculate and display FPS every 30 frames
        if frame_count % 30 == 0:
            elapsed_time = time.time() - start_time
            current_fps = 30 / elapsed_time if elapsed_time > 0 else 0
            print(f"Current FPS: {current_fps:.2f}")
            start_time = time.time()
        
        # Process every frame for smooth experience
        processed_frame, detections = detection_system.process_frame(frame)
        detection_results = detections
        
        # Add FPS display on frame
        cv2.putText(processed_frame, f'FPS: {fps_counter/(time.time() - start_time + 0.001):.1f}', 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # High quality JPEG encoding for better performance
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # Good quality vs speed balance
        ret, buffer = cv2.imencode('.jpg', processed_frame, encode_params)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/start_stream', methods=['POST'])
def start_stream():
    """Start video stream."""
    global is_streaming
    
    if is_streaming:
        return jsonify({'status': 'error', 'message': 'Stream already running'})
    
    try:
        return jsonify({'status': 'success', 'message': 'Stream started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_stream', methods=['POST'])
def stop_stream():
    """Stop video stream."""
    global is_streaming, camera
    is_streaming = False
    
    if camera:
        camera.release()
        camera = None
    
    return jsonify({'status': 'success', 'message': 'Stream stopped'})

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/detections')
def get_detections():
    """Get current detection results."""
    return jsonify(detection_results)

@app.route('/api/fps')
def get_fps():
    """Get current FPS information."""
    global fps_counter, start_time
    elapsed = time.time() - start_time + 0.001  # Avoid division by zero
    current_fps = fps_counter / elapsed if elapsed > 0 else 0
    return jsonify({
        'fps': round(current_fps, 2),
        'frame_count': fps_counter,
        'elapsed_time': round(elapsed, 2)
    })

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload and process image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'})
    
    try:
        # Read and process image
        image = Image.open(file.stream)
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Process frame
        processed_frame, detections = detection_system.process_frame(frame)
        
        # Convert back to RGB for web display
        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        processed_image = Image.fromarray(processed_frame)
        
        # Convert to base64
        buffered = BytesIO()
        processed_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'processed_image': f'data:image/jpeg;base64,{img_str}',
            'detections': detections
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)