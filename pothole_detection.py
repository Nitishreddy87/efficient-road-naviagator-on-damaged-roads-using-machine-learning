# Importing necessary libraries
import cv2 as cv
import time
import geocoder
import os
from datetime import datetime
import pyttsx3
import winsound   # 🔊 For beeps on Windows

# ✅ Base path (folder where main.py is located)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# ✅ Reading label names from obj.names file (absolute path)
names_path = os.path.join(BASE_PATH, "utils", "obj.names")
with open(names_path, "r") as f:
    class_name = [cname.strip() for cname in f.readlines()]

# ✅ Importing model weights and config file with absolute paths
weights_path = os.path.join(BASE_PATH, "utils", "yolov4_tiny.weights")
cfg_path = os.path.join(BASE_PATH, "utils", "yolov4_tiny.cfg")

net1 = cv.dnn.readNet(weights_path, cfg_path)

# 🔹 Force CPU instead of CUDA
net1.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net1.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

model1 = cv.dnn_DetectionModel(net1)
model1.setInputParams(size=(640, 480), scale=1/255, swapRB=True)

# ✅ Defining the video source (0 for camera or file name for video)
video_path = os.path.join(BASE_PATH, "test.mp4")
cap = cv.VideoCapture(video_path)

width = cap.get(3)
height = cap.get(4)

result_path = os.path.join(BASE_PATH, "result.avi")
result = cv.VideoWriter(result_path,
                         cv.VideoWriter_fourcc(*'MJPG'),
                         10, (int(width), int(height)))

# ✅ Defining parameters for result saving and coordinates
g = geocoder.ip('me')
pothole_dir = os.path.join(BASE_PATH, "pothole_coordinates")
os.makedirs(pothole_dir, exist_ok=True)  # ensure folder exists

starting_time = time.time()
Conf_threshold = 0.5
NMS_threshold = 0.4
frame_counter = 0
i = 0
b = 0

# 🔊 Text-to-Speech setup
engine = pyttsx3.init()
engine.setProperty('rate', 150)   # speed
engine.setProperty('volume', 1.0) # volume

def speak_warning(distance, severity):
    """Give different warnings with sound"""
    if distance <= 3:
        winsound.Beep(1000, 500)  # High pitch alarm
        message = f"⚠ Warning! Severe pothole very close, {distance:.1f} meters ahead! Severity {severity}"
    elif distance <= 6:
        winsound.Beep(600, 300)   # Medium beep
        message = f"Pothole ahead at {distance:.1f} meters. Severity {severity}"
    else:
        message = f"Pothole detected at {distance:.1f} meters ahead. Severity {severity}"
    
    engine.say(message)
    engine.runAndWait()

last_alert_time = 0
alert_cooldown = 3  # seconds

# Detection loop
while True:
    ret, frame = cap.read()
    frame_counter += 1
    if not ret:
        break

    # Run detection
    classes, scores, boxes = model1.detect(frame, Conf_threshold, NMS_threshold)

    for (classid, score, box) in zip(classes, scores, boxes):
        label = "pothole"
        x, y, w, h = box
        rec_area = w * h
        frame_area = width * height

        # Severity levels
        severity = "Low"
        if rec_area / frame_area > 0.1:
            severity = "High"
        elif rec_area / frame_area > 0.02:
            severity = "Medium"

        # Draw box + save pothole data
        if len(scores) != 0 and scores[0] >= 0.7:
            if (rec_area / frame_area) <= 0.1 and box[1] < 600:
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv.putText(frame, f"Severity: {severity}", (box[0], box[1] - 10),
                           cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

                # 🛑 Example distance estimation (simple proportional)
                distance = 10 - (w / 50)
                if distance < 0: distance = 1

                cv.putText(frame, f"{distance:.1f}m", (x, y + h + 20),
                           cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

                # 🔊 Speak warning (with cooldown)
                current_time = time.time()
                if current_time - last_alert_time > alert_cooldown:
                    speak_warning(distance, severity)
                    last_alert_time = current_time

                # Save images + text at intervals
                pothole_img = os.path.join(pothole_dir, f'pot{i}.jpg')
                pothole_txt = os.path.join(pothole_dir, f'pot{i}.txt')

                if i == 0:
                    cv.imwrite(pothole_img, frame)
                    with open(pothole_txt, 'w') as f:
                        f.write(str(g.latlng) + f"\nSeverity: {severity}")
                    i += 1

                elif (time.time() - b) >= 2:
                    cv.imwrite(pothole_img, frame)
                    with open(pothole_txt, 'w') as f:
                        f.write(str(g.latlng) + f"\nSeverity: {severity}")
                    b = time.time()
                    i += 1

    # FPS overlay
    endingTime = time.time() - starting_time
    fps = frame_counter / endingTime
    cv.putText(frame, f'FPS: {fps:.2f}', (20, 50),
               cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

    # Show + save video
    cv.imshow('frame', frame)
    result.write(frame)

    key = cv.waitKey(1)
    if key == ord('q'):
        break

# Cleanup
cap.release()
result.release()
cv.destroyAllWindows()
