"""
Legal Compass — Database Layer
SQLite persistence for conversation history and session management.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "legal_compass.db"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT    NOT NULL,
            user_msg    TEXT    NOT NULL,
            bot_resp    TEXT    NOT NULL,
            category    TEXT    DEFAULT 'general',
            timestamp   TEXT    DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id  TEXT    PRIMARY KEY,
            created_at  TEXT    DEFAULT (datetime('now', 'localtime')),
            msg_count   INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_conv_session
            ON conversations(session_id);
    """)
    conn.commit()
    conn.close()
    print("[DB] SQLite initialized →", DB_PATH)


def save_conversation(
    session_id: str,
    user_msg: str,
    bot_resp: str,
    category: str = "general",
):
    """Persist a single Q&A pair."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO conversations (session_id, user_msg, bot_resp, category)"
        " VALUES (?, ?, ?, ?)",
        (session_id, user_msg, bot_resp, category),
    )
    c.execute(
        """
        INSERT INTO sessions (session_id, msg_count) VALUES (?, 1)
        ON CONFLICT(session_id)
        DO UPDATE SET msg_count = msg_count + 1
        """,
        (session_id,),
    )
    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 50) -> list:
    """Return the last `limit` messages for a session (chronological order)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT user_msg, bot_resp, category, timestamp
        FROM conversations
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {"user": r[0], "bot": r[1], "category": r[2], "timestamp": r[3]}
        for r in reversed(rows)
    ]


def clear_history(session_id: str):
    """Delete all messages for a session."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Return aggregate statistics across all sessions."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM conversations")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT session_id) FROM conversations")
    users = c.fetchone()[0]
    c.execute("SELECT category, COUNT(*) FROM conversations GROUP BY category")
    cats = dict(c.fetchall())
    conn.close()
    return {"total_queries": total, "unique_users": users, "by_category": cats}
