import cv2

for i in range(5):  # tries index 0, 1, 2, 3, 4
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera found at index {i}")
        cap.release()
    else:
        print(f"No camera at index {i}")