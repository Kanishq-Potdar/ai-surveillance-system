import cv2
from ultralytics import YOLO
from datetime import datetime
import sqlite3
import threading
from alerter import send_email_alert
import pygame
pygame.mixer.init()

# ── Database setup ────────────────────────────────────────────
conn = sqlite3.connect("surveillance.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp   TEXT,
        label       TEXT,
        confidence  REAL,
        camera_id   TEXT
    )
""")
conn.commit()

def log_event(label, confidence, camera_id="CAM_01"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO events (timestamp, label, confidence, camera_id) VALUES (?, ?, ?, ?)",
        (timestamp, label, round(confidence, 2), camera_id)
    )
    conn.commit()
    print(f"[{timestamp}] LOGGED: {label} ({confidence:.2f}) — {camera_id}")

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
cap   = cv2.VideoCapture("street.mp4")

WATCH_FOR        = ["person", "car", "backpack", "handbag"]
COOLDOWN_SECONDS = 3
last_logged      = {}
last_alerted     = {}   # separate cooldown tracker for alerts

while True:
    ret, frame = cap.read()

    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    results  = model(frame)
    annotated = results[0].plot()

    for box in results[0].boxes:
        label      = results[0].names[int(box.cls)]
        confidence = float(box.conf)

        if label in WATCH_FOR and confidence > 0.5:
            now = datetime.now()

            # Log to database with cooldown
            last_time = last_logged.get(label)
            if last_time is None or (now - last_time).seconds >= COOLDOWN_SECONDS:
                log_event(label, confidence)
                last_logged[label] = now

            # Sound alert with its own cooldown (10 seconds so it's not annoying)
            # Sound + email alert with cooldown
            last_alert_time = last_alerted.get(label)
            if label in HIGH_PRIORITY:
                if last_alert_time is None or (now - last_alert_time).seconds >= 10:
                    # Sound alert
                    play_alert()
                    last_alerted[label] = now
                    print(f"🔔 ALERT: {label} detected!")

                    # Email alert in background thread (so video doesn't freeze)
                    # Only email every 60 seconds to avoid inbox spam
                    last_email_time = last_alerted.get(label + "_email")
                    if last_email_time is None or (now - last_email_time).seconds >= 60:
                        threading.Thread(
                            target=send_email_alert,
                            args=(label, confidence, "CAM_01"),
                            daemon=True
                        ).start()
                        last_alerted[label + "_email"] = now

    cv2.imshow("AI Surveillance", annotated)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()