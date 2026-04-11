import json
import sqlite3
import os
from config import SYSTEM_PROMPT

DB_FILE = "data/sessions.db"

def get_db_connection():
    """Establish database connection and enable foreign key constraints."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize the database and create 'sessions' and 'messages' tables."""
    with get_db_connection() as conn:
        # 1. User settings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                chat_id TEXT PRIMARY KEY,
                api_key TEXT,
                total_tokens INTEGER DEFAULT 0,
                file_buffer TEXT DEFAULT '[]'
            )
        """)
        # 2. Conversation history table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES sessions (chat_id) ON DELETE CASCADE
            )
        """)
        conn.commit()

# Initialize the database immediately upon startup
init_db()

def get_session(chat_id):
    """Retrieve user settings and all conversation history in one go using a JOIN."""
    cid = str(chat_id)
    with get_db_connection() as conn:
        # Use LEFT JOIN to ensure session settings are retrieved even if no messages exist
        query = """
            SELECT s.api_key, s.total_tokens, s.file_buffer, m.role, m.content
            FROM sessions s
            LEFT JOIN messages m ON s.chat_id = m.chat_id
            WHERE s.chat_id = ?
            ORDER BY m.id ASC
        """
        rows = conn.execute(query, (cid,)).fetchall()

        if not rows:
            # If no session exists, initialize a new user
            conn.execute("INSERT INTO sessions (chat_id, api_key, total_tokens) VALUES (?, ?, ?)",
                         (cid, None, 0))
            conn.execute("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                         (cid, "system", SYSTEM_PROMPT))
            conn.commit()
            # Query again to get the newly created session
            rows = conn.execute(query, (cid,)).fetchall()

        # Since JOIN produces multiple rows (one per message),
        # we organize them into a single session dictionary
        first_row = rows[0]
        session = {
            "chat_id": cid,
            "api_key": first_row["api_key"],
            "total_tokens": first_row["total_tokens"],
            "messages": [],
            "file_buffer": json.loads(first_row["file_buffer"])
        }

        for row in rows:
            if row["role"]: # Exclude cases where no message exists
                session["messages"].append({"role": row["role"], "content": row["content"]})

        # If there are no messages, add the system prompt
        if not session["messages"]:
            session["messages"].append({"role": "system", "content": SYSTEM_PROMPT})

        return session

def add_message(chat_id, role, content):
    """Add a new message to the database (replacing the previous save_session overwrite mode)."""
    cid = str(chat_id)
    with get_db_connection() as conn:
        conn.execute("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                     (cid, role, content))
        conn.commit()

def update_session_stats(chat_id, api_key=None, total_tokens=None):
    """Update user settings or token count."""
    cid = str(chat_id)
    with get_db_connection() as conn:
        if api_key is not None:
            conn.execute("UPDATE sessions SET api_key = ? WHERE chat_id = ?", (api_key, cid))
    if total_tokens is not None:
        conn.execute("UPDATE sessions SET total_tokens = ? WHERE chat_id = ?", (total_tokens, cid))
        conn.commit()

def update_api_key(chat_id, api_key):
    """Update the API Key."""
    update_session_stats(chat_id, api_key=api_key)

def save_total_tokens(chat_id, total_tokens):
    update_session_stats(chat_id, total_tokens=total_tokens)

def save_session(chat_id, session):
    cid = str(chat_id)
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE sessions SET api_key = ?, total_tokens = ?, file_buffer = ? WHERE chat_id = ?",
            (session["api_key"], session["total_tokens"],
             json.dumps(session["file_buffer"]), cid)
        )
        conn.commit()

def clear_session(chat_id):
    """Clear all conversation history while retaining the API Key."""
    cid = str(chat_id)
    with get_db_connection() as conn:
        # Delete all messages for the user
        conn.execute("DELETE FROM messages WHERE chat_id = ?", (cid,))
        # Re-insert the System Prompt
        conn.execute("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                     (cid, "system", SYSTEM_PROMPT))
        # Reset token count and file buffer
        conn.execute("UPDATE sessions SET total_tokens = 0, file_buffer = '[]' WHERE chat_id = ?", (cid,))
        conn.commit()

def slide_window(chat_id, threshold):
    """
    Sliding window: Directly delete the oldest records from the database.
    Note: The chat_id is passed here instead of the session object.
    """
    cid = str(chat_id)
    # Logic: If total_tokens is too high, delete the two oldest messages (user + assistant)
    # until tokens are below the threshold (simplified to deleting two records per call).
    with get_db_connection() as conn:

        oldest_ids = conn.execute(
            "SELECT id FROM messages WHERE chat_id = ? AND role != 'system' ORDER BY id ASC LIMIT 2",
            (cid,)
        ).fetchall()

        if oldest_ids:
            ids_to_delete = tuple(row['id'] for row in oldest_ids)
            conn.execute(f"DELETE FROM messages WHERE id IN {ids_to_delete}")
            conn.commit()