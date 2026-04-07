import sqlite3
from datetime import datetime

DB_NAME = "chat_history.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            user_id TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_message(user_name, user_id, channel_id, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (user_name, user_id, channel_id, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_name,
        str(user_id),
        str(channel_id),
        content,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_recent_messages(channel_id, limit=20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_name, content, timestamp
        FROM messages
        WHERE channel_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (str(channel_id), limit))

    rows = cursor.fetchall()
    conn.close()

    rows.reverse()
    return rows


def build_context(channel_id, limit=15):
    rows = get_recent_messages(channel_id, limit)

    if not rows:
        return "No recent context"

    return "\n".join([f"{user}: {msg}" for user, msg, _ in rows])