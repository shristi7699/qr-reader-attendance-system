import os
import csv
import datetime
import time
import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Read the authorized users and their details from the file
user_data = {}
with open('./users.txt', 'r') as f:
    for line in f.readlines():
        user_id, user_name, user_class = line.strip().split(',')
        user_data[user_id] = {'name': user_name, 'class': user_class}

csv_file = './attendance.csv'

# Check if the CSV file exists, if not create it with headers
if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Username', 'Name', 'Class', 'In-Time', 'Out-Time'])

# Initialize the camera
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit(1)

# Track user states and attendance records
most_recent_access = {}
user_states = {}
attendance_records = {}
time_between_logs_th = 5

while True:
    ret, frame = cap.read()

    if not ret or frame is None:
        print("Error: Failed to capture a frame.")
        continue

    qr_info = decode(frame)

    if len(qr_info) > 0:
        qr = qr_info[0]
        data = qr.data.decode()
        rect = qr.rect
        polygon = qr.polygon

        if data in user_data:
            current_time = time.time()
            user_name = user_data[data]['name']
            user_class = user_data[data]['class']

            if data in most_recent_access and current_time - most_recent_access[data] < time_between_logs_th:
                cv2.putText(frame, f'{user_name}', (rect.left, rect.top - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                cv2.putText(frame, 'Attendence Submitted', (rect.left, rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
            else:
                most_recent_access[data] = current_time

                if data in user_states and user_states[data] == "IN":
                    user_states[data] = "OUT"
                    out_time = datetime.datetime.now()
                    status = "OUT"

                    if data in attendance_records:
                        with open(csv_file, 'r') as f:
                            rows = list(csv.reader(f))
                        rows[attendance_records[data]][4] = out_time
                        with open(csv_file, 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerows(rows)
                else:
                    user_states[data] = "IN"
                    in_time = datetime.datetime.now()
                    status = "IN"

                    with open(csv_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        row_index = sum(1 for _ in open(csv_file))  # Calculate row index
                        attendance_records[data] = row_index
                        writer.writerow([data, user_name, user_class, in_time, ''])

                cv2.putText(frame, f'{user_name}', (rect.left, rect.top - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                cv2.putText(frame, 'Attendance recorded', (rect.left, rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        else:
            cv2.putText(frame, 'ACCESS DENIED', (rect.left, rect.top - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        frame = cv2.rectangle(frame, (rect.left, rect.top),
                              (rect.left + rect.width, rect.top + rect.height),
                              (0, 255, 0), 5)
        frame = cv2.polylines(frame, [np.array(polygon)], True, (255, 0, 0), 5)

    cv2.imshow('webcam', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
