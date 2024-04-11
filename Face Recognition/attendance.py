import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import requests
import subprocess

# URL for sending attendance data
url = 'http://localhost:8080/mark/markpresent'

# File to store attendance
file_name = datetime.now().strftime('%d_%m_%Y.csv')

# Directory containing images
path = 'images'

# Load images and extract names
images = []
personNames = []
for img_name in os.listdir(path):
    img_path = os.path.join(path, img_name)
    current_img = cv2.imread(img_path)
    images.append(current_img)
    personNames.append(os.path.splitext(img_name)[0])

# Extract student details from names
student_details = [name.split("_")[:3] for name in personNames]

# Function to encode faces in images
def faceEncodings(images):
    print("Encoding images, please wait...")
    encodeList = []
    for img in images:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img_rgb)[0]
        encodeList.append(encode)
    print("Encoding completed.")
    return encodeList

# Function to mark attendance
def markAttendance(roll, name, branch):
    with open(file_name, 'a+') as f:
        f.seek(0)
        if name not in f.read():
            current_time = datetime.now().strftime('%H:%M:%S')
            current_date = datetime.now().strftime('%Y-%m-%d')
            data = {
                "rollno": roll,
                "name": name,
                "branch": branch,
                "time": current_time,
                "date": current_date
            }
            # Send data to server
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print(f"Attendance marked for {name}")
                # Run mark_attendance.py script
                subprocess.run(["python", "mark_attendance.py"])
            else:
                print("Failed to mark attendance.")
            # Write to local file
            f.write(f'\n{name}, Roll: {roll}, Branch: {branch}, Time: {current_time}, Date: {current_date}')

# Encode known faces
encodeListKnown = faceEncodings(images)

# Start capturing video
print('Starting camera...')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture frame")
        break
    
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
        face_distances = face_recognition.face_distance(encodeListKnown, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            try:
                roll, name, branch = student_details[best_match_index]
                top, right, bottom, left = face_location
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Draw a label with the name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Mark attendance
                markAttendance(roll, name, branch)
            except ValueError:
                print("Error: Invalid student details")

    # Display the resulting image
    cv2.imshow('Video', frame)
    
    # Handle keyboard events
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Save frame to file if 's' is pressed
        file_name = f"captured_frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(file_name, frame)
        print(f"Frame saved as {file_name}")

# Release handle to the webcam
cap.release()
cv2.destroyAllWindows()
