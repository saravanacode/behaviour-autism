import cv2
import numpy as np
import face_recognition
from ultralytics import YOLO
from sort import *
import tensorflow as tf
from tensorflow.keras.models import load_model
import cvzone
import math
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

columns = ["ID", "Name", "Behavior", "Start Time", "End Time", "Time"]
data = pd.DataFrame(columns=columns)  # Initialize DataFrame with the "Time" column

path = 'photos'
images = []
class_names = []
myList = os.listdir(path)
print(myList)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    class_names.append(os.path.splitext(cl)[0])
    print(class_names)


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)
prev_frame = datetime.now()

# Load Behavioral Detection Model
#behavioral_model = load_model("model.h5")  # Replace with the correct path
behavioral_model = load_model("model.h5", compile=False)
#behavioral_model.compile(optimizer=Adam(learning_rate=0.001), loss='your_loss_function', metrics=['accuracy'])
print("save")

CLASSES_LIST = ["SittingInChair&Active", "Bitting", "Fighting", "Running", "SittingInChair&IN-Active", "HandFlapping"]

model = YOLO("yolov5s.pt")

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

# Tracking
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Define constants based on the expected input shape of the behavioral model
SEQUENCE_LENGTH = 20
FRAME_SIZE = (64, 64, 3)

# Dictionary to store start times for each person and each behavior
start_times_behavior = {}

while True:
    success, img = cap.read()
    facesCurFrame = face_recognition.face_locations(img)
    encodesCurFrame = face_recognition.face_encodings(img, facesCurFrame)

    results = model(img, stream=True)
    detections = np.empty((0, 5))

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bounding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            # Confidence
            conf = math.ceil((box.conf[0] * 100)) / 100
            # Class Name
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass == "person" and conf > 0.3:
                currentArray = np.array([x1, y1, x2, y2, conf])
                detections = np.vstack((detections, currentArray))

    # Update tracker with YOLO detections
    resultsTracker = tracker.update(detections)

    # Process each tracked object
    for result in resultsTracker:
        x1, y1, x2, y2, id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        id = int(id)  # Cast id to integer

        # Crop, Resize, and Normalize ROI for Behavioral Detection
        roi = img[y1:y2, x1:x2]
        resized_roi = cv2.resize(roi, (FRAME_SIZE[1], FRAME_SIZE[0]))
        normalized_roi = resized_roi / 255
        # Repeat the frame to create a sequence
        sequence = np.array([normalized_roi] * SEQUENCE_LENGTH)

        # Perform Behavioral Detection
        behavioral_predictions = behavioral_model.predict(np.expand_dims(sequence, axis=0))

        # Get the predicted class and confidence
        predicted_class = np.argmax(behavioral_predictions)
        confidence = behavioral_predictions[0, predicted_class]

        # Set a confidence threshold (e.g., 0.5)
        confidence_threshold = 0.5

        # Check if the predicted class has sufficient confidence
        if confidence > confidence_threshold:
            # Face recognition
            if encodesCurFrame:
                faceDis = face_recognition.face_distance(encodeListKnown, encodesCurFrame[0])
                matchIndex = np.argmin(faceDis)
                if faceDis[matchIndex] < 0.50:
                    name = class_names[matchIndex].upper()
                else:
                    name = 'Unknown'
            else:
                name = 'Unknown'

            # Display bounding box and behavior
            w, h = x2 - x1, y2 - y1
            cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255))

            # Check if this is the first time detecting this person and behavior
            if (id, predicted_class) not in start_times_behavior:
                start_times_behavior[(id, predicted_class)] = datetime.now()

                # Add a new row to the DataFrame for the start time
                data = pd.concat(
                    [data, pd.DataFrame([[id, name, CLASSES_LIST[predicted_class], datetime.now(), None, 0]],
                                        columns=columns)], ignore_index=True)

            # Calculate elapsed time for the person and the behavior
            elapsed_time_behavior = (datetime.now() - start_times_behavior[(id, predicted_class)]).total_seconds()

            # Update the existing record with the current time
            data.loc[(data['ID'] == id) & (data['Behavior'] == CLASSES_LIST[predicted_class]) & (
                data['End Time'].isnull()), 'End Time'] = datetime.now()
            data.loc[(data['ID'] == id) & (data['Behavior'] == CLASSES_LIST[predicted_class]) & (
                data['End Time'].isnull()), 'Time'] += elapsed_time_behavior

            cvzone.putTextRect(img,
                               f'ID: {name} - Behavior: {CLASSES_LIST[predicted_class]} - '
                               f'Time Behavior: {elapsed_time_behavior:.2f}s',
                               (max(0, x1), max(35, y1)),
                               scale=1, thickness=1, offset=5)

            cx, cy = x1 + w // 2, y1 + h // 2
            cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

    # Display FPS
    current_frame = datetime.now()
    fps = 1 / ((current_frame - prev_frame).total_seconds())
    prev_frame = current_frame
    cv2.putText(img, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    data_sorted = data.sort_values(by='ID')

    # Save the sorted DataFrame to a CSV file
    data_sorted.to_csv("behavior_info.csv", index=False)

    # Plotting the pie chart
    plt.figure(figsize=(6, 6))
    behavior_counts = data['Behavior'].value_counts()
    plt.pie(behavior_counts, labels=behavior_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Behavior Distribution')

    # Save the pie chart to an image file (e.g., PNG)
    plt.savefig('behavior_pie_chart.png')

    # Display the output
    cv2.imshow("Integrated Detection", img)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
