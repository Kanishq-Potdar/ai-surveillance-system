import cv2
from ultralytics import YOLO
from datetime import datetime
import sqlite3

# ── Database setup ──────────────────────────────────────────
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

# ── Detection ────────────────────────────────────────────────
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("street.mp4")

WATCH_FOR = ["person", "car", "backpack", "handbag"]

# Cooldown tracker — avoid logging same object 30 times per second
last_logged = {}
COOLDOWN_SECONDS = 3

while True:
    ret, frame = cap.read()

    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    results = model(frame)
    annotated = results[0].plot()

    for box in results[0].boxes:
        label = results[0].names[int(box.cls)]
        confidence = float(box.conf)

        if label in WATCH_FOR and confidence > 0.5:
            now = datetime.now()
            last_time = last_logged.get(label)

            # Only log if we haven't logged this label in the last 3 seconds
            if last_time is None or (now - last_time).seconds >= COOLDOWN_SECONDS:
                log_event(label, confidence)
                last_logged[label] = now

    cv2.imshow("AI Surveillance", annotated)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()