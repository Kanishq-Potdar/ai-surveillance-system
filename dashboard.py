from flask import Flask, jsonify, render_template
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

if __name__ == "__main__":
    app.run(debug=True)