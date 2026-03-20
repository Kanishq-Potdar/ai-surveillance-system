import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()

# ── Your email config ─────────────────────────────────────────

SENDER_EMAIL    = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL  = os.getenv("RECEIVER_EMAIL")

def send_email_alert(label, confidence, camera_id):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build the email
        msg = MIMEMultipart()
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = RECEIVER_EMAIL
        msg["Subject"] = f"🚨 Surveillance Alert — {label} detected"

        body = f"""
AI Surveillance System Alert
-----------------------------
Event     : {label} detected
Confidence: {confidence:.0%}
Camera    : {camera_id}
Time      : {timestamp}

This is an automated alert from your surveillance system.
        """

        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail and send
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()                                    # encrypts the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        print(f"📧 Email alert sent for: {label}")

    except Exception as e:
        print(f"Email failed: {e}")