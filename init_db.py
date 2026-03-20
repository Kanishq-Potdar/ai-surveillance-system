# ── Events Database setup ─────────────────────────────────────────
import sqlite3


def init_events_db():
    conn = sqlite3.connect("surveillance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            label TEXT,
            confidence REAL,
            camera_id TEXT
        )
    """)
    conn.commit()
    conn.close()

    # ── Users Database setup ─────────────────────────────────────────
def init_users_db():
    conn = sqlite3.connect("surveillance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT default 'viewer',
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    conn.commit()
    conn.close()
    
# Called by detect.py to initialize both databases at startup

def init_db():
    init_events_db()
    init_users_db()