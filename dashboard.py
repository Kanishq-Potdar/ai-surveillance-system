from flask import Flask, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_bcrypt import Bcrypt
from auth import auth, User, bcrypt
from init_db import init_db
from collections import Counter
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production!

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id): 
    conn = sqlite3.connect("surveillance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], role=user[2])
    return None

app.register_blueprint(auth)
bcrypt.init_app(app)

init_db()  # Ensure database is initialized before starting the app

def get_events():
    conn = sqlite3.connect("surveillance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "id":         row[0],
            "timestamp":  row[1],
            "label":      row[2],
            "confidence": row[3],
            "camera_id":  row[4]
        })
    return events

@app.route("/")
@login_required
def home():
    # Now serves the HTML file instead of plain text
    return render_template("index.html", username=current_user.username, role=current_user.role)

@app.route("/events")
@login_required
def events():
    return jsonify(get_events())

@app.route("/stats")
@login_required
def stats():
    conn = sqlite3.connect("surveillance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT label, COUNT(*) FROM events GROUP BY label")
    label_counts = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT strftime('%H:00', timestamp) as hour, COUNT(*) 
        FROM events 
        GROUP BY hour 
        ORDER BY hour
    """)
    hourly = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT camera_id, COUNT(*) FROM events GROUP BY camera_id")
    camera_counts = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return jsonify({
        "label_counts":  label_counts,
        "hourly":        hourly,
        "camera_counts": camera_counts
    })

@app.route("/charts")
@login_required
def charts():
    if current_user.role == "viewer":
        return redirect(url_for("home"))
    return render_template("charts.html")


if __name__ == "__main__":
    app.run(debug=True)