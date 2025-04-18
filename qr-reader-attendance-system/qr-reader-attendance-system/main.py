import os
import cv2
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
import numpy as np

# Path to the directory containing QR code images
input_dir = r"C:\Users\palp3\OneDrive\Pictures\Desktop\qr-reader-attendance-system\qr-reader-attendance-system\data\qrcodes"

# Check if the directory exists
if not os.path.exists(input_dir):
    print(f"Error: The directory '{input_dir}' does not exist.")
    exit(1)

# Process images in the directory
for j in sorted(os.listdir(input_dir)):
    img_path = os.path.join(input_dir, j)
    if os.path.isfile(img_path) and img_path.lower().endswith(('.png', '.jpg', '.jpeg')):  # Ensure it's a valid image file
        img = cv2.imread(img_path)

        if img is None:
            print(f"Error: Unable to read the image file '{j}'.")
            continue

        qr_info = decode(img)

        if not qr_info:
            print(f"No QR code detected in file: {j}")
            continue

        for qr in qr_info:
            data = qr.data
            rect = qr.rect
            polygon = qr.polygon

            print(f"Data: {data.decode()}")
            print(f"Rectangle: {rect}")
            print(f"Polygon: {polygon}")

            img = cv2.rectangle(img, (rect.left, rect.top), 
                                (rect.left + rect.width, rect.top + rect.height),
                                (0, 255, 0), 5)

            img = cv2.polylines(img, [np.array(polygon)], True, (255, 0, 0), 5)

            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.show()
    else:
        print(f"Skipping non-file entry: {j}")
