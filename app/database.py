import sqlite3
import os
from datetime import datetime

# Path to database file
DB_PATH = os.path.join("data", "messages.db")


def get_connection():
    """Establish connection to SQLite database."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """Initialize database tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                text TEXT NOT NULL,
                urgency TEXT NOT NULL,
                category TEXT,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_summarized BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
    print("📦 Database initialized successfully.")


def save_message(channel_id: str, user_id: str, text: str, urgency: str, category: str, reason: str):
    """Save classified non-urgent message into database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (channel_id, user_id, text, urgency, category, reason, is_summarized)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (channel_id, user_id, text, urgency, category, reason))
        conn.commit()
        return cursor.lastrowid


def get_unsummarized_messages():
    """Fetch all pending non-urgent messages that haven't been summarized yet."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, channel_id, user_id, text, category, reason, timestamp
            FROM messages
            WHERE is_summarized = 0 AND urgency = 'NON_URGENT'
            ORDER BY timestamp ASC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def mark_messages_as_summarized(message_ids: list):
    """Mark a list of message IDs as summarized."""
    if not message_ids:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in message_ids)
        cursor.execute(f"""
            UPDATE messages
            SET is_summarized = 1
            WHERE id IN ({placeholders})
        """, message_ids)
        conn.commit()


# Self-testing script
if __name__ == "__main__":
    init_db()
    msg_id = save_message(
        channel_id="C12345",
        user_id="U67890",
        text="Coffee break?",
        urgency="NON_URGENT",
        category="Social",
        reason="Casual prompt"
    )
    print(f"✅ Test message saved with ID: {msg_id}")

    pending = get_unsummarized_messages()
    print(f"📊 Pending unsummarized messages count: {len(pending)}")
