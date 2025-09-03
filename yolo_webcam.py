
import os
import time
import cv2
import numpy as np
import torch

# Load YOLOv8 model using Ultralytics
from ultralytics import YOLO
import torchvision.models as models
import torch.nn as nn
from torchvision.models import ResNet18_Weights

# Initialize YOLOv8 for person detection
FaceDetector = YOLO('yolov8n.pt')

# File path for the ResNet-18 age/gender model (the one that works)
age_model_path = os.path.abspath('models/ResNet-18 Age 0.60 + Gender 93 (1).pt')

if not os.path.exists(age_model_path):
    raise FileNotFoundError(f"ResNet-18 model file not found: {age_model_path}")

# Age classification parameters
Classes = 9
Groups = ['00-10', '11-20', '21-30',
          '31-40', '41-50', '51-60',
          '61-70', '71-80', '81-90']

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# Load ResNet-18 model for age/gender classification
resnet_base = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
resnet_base.fc = nn.Linear(512, Classes+2)
resnet_model = nn.Sequential(resnet_base)
resnet_model.load_state_dict(torch.load(age_model_path, map_location=device))
resnet_model.eval()
resnet_model.to(device)

def classify_age_gender(face_img):
    """Classify age and gender using ResNet-18 model."""
    # Preprocess face_img for ResNet-18 model
    img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img_rgb, (200, 200))
    img = torch.tensor(img, dtype=torch.float32).permute(2, 0, 1) / 255.0
    img = img.unsqueeze(0).to(device)

    with torch.no_grad():
        logits = resnet_model(img)[0]
        age_idx = torch.argmax(logits[:Classes]).item()
        gender_idx = torch.argmax(logits[Classes:]).item()
        
        age_label = Groups[age_idx] if 0 <= age_idx < Classes else "Unknown"
        gender = 'Male' if gender_idx == 0 else 'Female'

    return gender, age_label

def draw_text_with_background(frame, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.7, color=(0, 255, 0), thickness=2, bg_color=(0, 0, 0), bg_padding=5):
    """Draw text with background on the frame."""
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Draw background rectangle
    top_left = (position[0] - bg_padding, position[1] - text_height - bg_padding)
    bottom_right = (position[0] + text_width + bg_padding, position[1] + baseline + bg_padding)
    cv2.rectangle(frame, top_left, bottom_right, bg_color, cv2.FILLED)
    
    # Draw text on top of the rectangle
    cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

def select_camera():
    """Check available cameras and allow the user to select one."""
    index = 0
    available_cameras = []
    
    while True:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
            index += 1
        else:
            break
    
    if not available_cameras:
        print("No cameras available.")
        return None
    
    print("Available cameras:", available_cameras)
    
    try:
        camera_index = int(input(f"Enter the camera index (0 to {len(available_cameras) - 1}): "))
        if camera_index not in available_cameras:
            raise ValueError("Invalid camera index.")
    except ValueError:
        print("Invalid input. Please enter a valid camera index.")
        return None
    
    return camera_index

def main():
    """Main function to run the video processing."""
    output_dir = 'output_videos'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    camera_index = select_camera()
    if camera_index is None:
        return

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: Could not open selected camera.")
        return

    # Get screen resolution
    screen_res = (1280, 720)  # Set to a common resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_res[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_res[1])

    # Create output video file
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(os.path.join(output_dir, 'output.avi'), fourcc, 20.0, screen_res)

    path_points = []
    last_path_update_time = time.time()
    previous_person_centers = {}



    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        # YOLOv8 detection using Ultralytics
        results = FaceDetector(frame)
        boxes = results[0].boxes.data.cpu().numpy()  # [N, 6] (x1, y1, x2, y2, conf, cls)

        annotated_frame = frame.copy()
        processed_faces = set()

        for box in boxes:
            x1, y1, x2, y2, score, cls = box
            print(f"Detected box: {x1}, {y1}, {x2}, {y2}, score: {score}, class: {cls}")
            if score < 0.3:
                continue
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            label = int(cls)
            # Assuming class 0 is 'person'. Adjust if needed.
            if label == 0:
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                face_img = frame[y1:y2, x1:x2]
                print(f"Face crop shape: {face_img.shape}")
                if face_img.size > 0:
                    face_key = (x1, y1, x2, y2)
                    if face_key not in processed_faces:
                        try:
                            gender, age = classify_age_gender(face_img)
                            processed_faces.add(face_key)
                            text_x = x2 + 10
                            text_y = y1 + 20
                            draw_text_with_background(annotated_frame, f'Age: {age}', (text_x, text_y), font_scale=0.7, color=(0, 255, 0), bg_color=(0, 0, 0))
                            draw_text_with_background(annotated_frame, f'Gender: {gender}', (text_x, text_y + 30), font_scale=0.7, color=(0, 255, 0), bg_color=(0, 0, 0))
                        except Exception as e:
                            print(f"Error processing face: {e}")

        out.write(annotated_frame)

        # Display the resulting frame in a window
        cv2.imshow('YOLOv8 Object Detection', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
