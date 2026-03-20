import cv2
from ultralytics import YOLO
from datetime import datetime
import sqlite3
import threading
from alerter import send_email_alert
import pygame
pygame.mixer.init()
from init_db import init_db


def log_event(label, confidence, camera_id="CAM_01"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("surveillance.db")
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (timestamp, label, confidence, camera_id) VALUES (?, ?, ?, ?)",
        (timestamp, label, round(confidence, 2), camera_id)
    )
    conn.commit()
    print(f"[{timestamp}] LOGGED: {label} ({confidence:.2f}) — {camera_id}")
    conn.close()

# ── Alert system ──────────────────────────────────────────────
# Objects that trigger a sound alert
HIGH_PRIORITY = ["person", "backpack", "handbag"]
ALERT_SOUND   = "alert.wav"   # must be in your project folder

def play_alert():
    def _play():
        pygame.mixer.music.load(ALERT_SOUND)
        pygame.mixer.music.play()
    threading.Thread(target=_play, daemon=True).start()

# ── Detection ─────────────────────────────────────────────────
model = YOLO("yolov8n.pt")

WATCH_FOR        = ["person", "car", "backpack", "handbag"]
COOLDOWN_SECONDS = 3
last_logged      = {}
last_alerted     = {}   # separate cooldown tracker for alerts

def redact_faces(frame, results):
    for box in results[0].boxes:
        label = results[0].names[int(box.cls)]
        if label == "person":
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            face_bottom = y1 + (y2 - y1) // 4  # Assume face is in upper 1/4 of the person box
            face_region = frame[y1:face_bottom, x1:x2]
            blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
            frame[y1:face_bottom, x1:x2] = blurred_face
    return frame

def run_camera(video_source, camera_id):
    cap   = cv2.VideoCapture(video_source)
    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results  = model(frame)
        frame = redact_faces(frame, results)
        annotated = results[0].plot(img =frame.copy())

        for box in results[0].boxes:
            label      = results[0].names[int(box.cls)]
            confidence = float(box.conf)

            if label in WATCH_FOR and confidence > 0.5:
                now = datetime.now()

                # Log to database with cooldown
                last_time = last_logged.get(label + camera_id)  # separate cooldown per camera
                if last_time is None or (now - last_time).seconds >= COOLDOWN_SECONDS:
                    log_event(label, confidence)
                    last_logged[label + camera_id] = now

                # Sound alert with its own cooldown (10 seconds so it's not annoying)
                # Sound + email alert with cooldown
                last_alert_time = last_alerted.get(label + camera_id)  # separate cooldown per camera
                if label in HIGH_PRIORITY:
                    if last_alert_time is None or (now - last_alert_time).seconds >= 10:
                        # Sound alert
                        play_alert()
                        last_alerted[label + camera_id] = now
                        print(f"🔔 ALERT: {label} detected!")

                        # Email alert in background thread (so video doesn't freeze)
                        # Only email every 60 seconds to avoid inbox spam
                        last_email_time = last_alerted.get(label + camera_id + "_email")
                        if last_email_time is None or (now - last_email_time).seconds >= 60:
                            threading.Thread(
                                target=send_email_alert,
                                args=(label, confidence, camera_id),
                                daemon=True
                            ).start()
                            last_alerted[label + camera_id + "_email" ] = now

        cv2.imshow(f"AI Surveillance - Camera {camera_id}", annotated)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

init_db()  # Ensure database is initialized before starting cameras

# Creating a thread
t1 = threading.Thread(target=run_camera, args=("street.mp4", "CAM_01"))
t2 = threading.Thread(target=run_camera, args=("street2.mp4", "CAM_02"))
t1.start()
t2.start()
t1.join()  # Wait for the thread to complete
t2.join()  # Wait for the thread to complete

cv2.destroyAllWindows()