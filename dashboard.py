from flask import Flask, jsonify, render_template
from collections import Counter
import sqlite3

app = Flask(__name__)

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
def home():
    # Now serves the HTML file instead of plain text
    return render_template("index.html")

@app.route("/events")
def events():
    return jsonify(get_events())

@app.route("/stats")
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
def charts():
    return render_template("charts.html")


if __name__ == "__main__":
    app.run(debug=True)