# AI-Powered Surveillance and Event Logging System

## Why I Built This

I was watching a crime show with my father and there was this scene where detectives
were going through hours of CCTV footage trying to find one person. It looked
painful. And I thought — why is someone still doing this manually? If you have a
description of a person, or their face, why can't you just ask the system to find
them?

That question turned into this project.

## What It Does Right Now

At its core this is a system designed to reduce manual watching of footage. Instead
of a guard staring at screens all day, the AI watches the feeds and generates alerts
when something worth noticing happens — like a person detected in an area they are
not supposed to be in.

Every detection gets logged automatically with a timestamp, confidence score, and
camera ID. A web dashboard lets you see everything in one place, search through past
events, and view detection trends over time. Faces are blurred automatically to keep
things privacy compliant.

It currently supports multiple cameras running simultaneously, sound and email
alerts, and role based access so different people see only what they need to.

## Where It's Going

The foundation is done but the more interesting work is still ahead. The idea is
to move beyond simple labels like "person detected" toward something more useful —
logs that actually describe what happened in plain English, generated automatically.
From there, a search bar that understands natural language queries would let you
type something like "show me all incidents near the entrance after 8pm" and get
real results back instead of scrolling through a table.

Eventually the goal is something closer to what sparked the idea — give the system
a description or a face and let it find the person across all footage automatically.
That part is still being figured out.

## How It All Fits Together

```
┌─────────────────────────────────────────────────────┐
│                    Video Sources                     │
│  [Camera 1]   [Camera 2]   [Camera N]  [RTSP Stream] │
└──────────────────────┬──────────────────────────────┘
                       │ frames
                       ▼
┌─────────────────────────────────────────────────────┐
│              AI Detection Engine (YOLOv8)            │
│     Detects: person, car, bag, restricted entry      │
│     Runs in parallel threads — one per camera        │
└───────┬──────────────────────────┬──────────────────┘
        │ events                   │ faces
        ▼                          ▼
┌───────────────┐         ┌─────────────────┐
│  Event Logger │         │  Face Redactor  │
│  SQLite DB    │         │  Blur for GDPR  │
└───────┬───────┘         └─────────────────┘
        │
        ├──────────────────────────┐
        ▼                          ▼
┌───────────────┐         ┌─────────────────┐
│ Alert System  │         │  Web Dashboard  │
│ Sound + Email │         │  Flask + Charts │
└───────────────┘         │  Role based     │
                          │  access control │
                          └─────────────────┘
```

## Built With

- Python 3.13
- YOLOv8 (Ultralytics) — the AI model doing the actual detection
- OpenCV — reads video feeds and handles the display
- SQLite — lightweight database, no setup needed
- Flask — runs the web dashboard
- Flask-Login + Flask-Bcrypt — handles authentication and password security
- Pygame — plays sound alerts
- Python-dotenv — keeps secrets out of the codebase

## Project Structure

```
ai-surveillance-system/
│
├── detect.py          — camera detection, event logging, alerts, face redaction
├── dashboard.py       — web server, protected routes, role based access
├── auth.py            — login, logout, register, user roles
├── init_db.py         — creates the database tables on first run
├── alerter.py         — handles sending email alerts
│
├── templates/
│   ├── index.html     — main dashboard with live event feed and search
│   ├── charts.html    — visual breakdown of detections over time
│   ├── login.html     — login page
│   └── register.html  — account registration page
│
├── .env               — your secrets and camera config (never committed)
└── .gitignore
```

## Getting Started

### 1. Clone the repo

```
git clone https://github.com/Kanishq-Potdar/ai-surveillance-system.git
cd ai-surveillance-system
```

### 2. Install dependencies

```
pip install ultralytics opencv-python flask flask-login flask-bcrypt pygame python-dotenv
```

### 3. Create your `.env` file

Create this manually in the project folder — it never gets committed to GitHub:

```
SECRET_KEY=pick-any-long-random-string
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-gmail-app-password
RECEIVER_EMAIL=where-alerts-should-go@gmail.com

# Point these at video files or live RTSP streams
CAM1_SOURCE=your_video_1.mp4
CAM2_SOURCE=your_video_2.mp4
```

For a real CCTV camera swap the video file for its RTSP stream address:

```
CAM1_SOURCE=rtsp://192.168.1.100:554/stream1
```

### 4. Adding more cameras

No hard limit on cameras — each one just needs a thread in `detect.py`:

```python
cam3 = os.getenv("CAM3_SOURCE", "camera3.mp4")
t3   = threading.Thread(target=run_camera, args=(cam3, "CAM_03"))
t3.start()
t3.join()
```

And a corresponding entry in `.env`:

```
CAM3_SOURCE=your_video_3.mp4
```

### 5. Run detection (Terminal 1)

```
python detect.py
```

### 6. Run dashboard (Terminal 2)

```
python dashboard.py
```

### 7. Open your browser

```
http://localhost:5000
```

Register an account and log in. Run both terminals at the same time —
they share the same database.

## Who Can See What

| Role   | Access                                           |
| ------ | ------------------------------------------------ |
| Admin  | Everything — events, charts, search, all cameras |
| Guard  | Live events and detection charts                 |
| Viewer | Read only event feed                             |

## How This Was Built

Built phase by phase, each adding a new layer:

- **Phase 1** — YOLOv8 running on a video file, bounding boxes drawn,
  detections logged to SQLite
- **Phase 2** — Sound alerts via Pygame, email alerts via Gmail SMTP
- **Phase 3** — Flask dashboard with live event feed, search, and stats
- **Phase 4** — Charts showing detections per hour, object breakdown,
  camera activity
- **Phase 5** — Multi-camera support using Python threading
- **Phase 6** — Face redaction using YOLO person bounding boxes
- **Phase 7** — User authentication, role based access, secrets moved
  to environment variables

## What's Next

- **Gemini/AI integration** — generate natural language descriptions of
  events instead of just labels, and a search bar that understands plain
  English queries
- **Person search** — describe someone or upload a face and find them
  across all footage automatically
- **IoT integration** — connect with door sensors, motion detectors,
  and other building systems
- **Edge deployment** — run detection on device without needing internet
- **Mobile alerts** — push notifications to a phone instead of just email
