import json
import os
import threading
from config import SYSTEM_PROMPT

DATA_FILE = "data/sessions.json"
file_lock = threading.Lock()
user_sessions = {}

def load_sessions():
    """Get memories and setting from JSON"""
    global user_sessions
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_sessions = json.load(f)
    else:
        os.makedirs("data", exist_ok=True)
        user_sessions = {}

load_sessions()

def save_sessions():
    """Save the current memories and personal API key into JSON"""
    with file_lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_sessions, f, ensure_ascii=False, indent=2)

def get_session(chat_id):
    """Get user session, initialize a clean state if it does not exist"""
    cid = str(chat_id)
    if cid not in user_sessions:
        user_sessions[cid] = {
            # 💡 reserve system prompt
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}], 
            "total_tokens": 0,
            "api_key": None,
            "file_buffer": []
        }
        save_sessions()
    return user_sessions[cid]

def update_api_key(chat_id, api_key):
    """Update the personal API Key"""
    session = get_session(chat_id)
    session["api_key"] = api_key
    save_sessions()

def clear_session(chat_id):
    cid = str(chat_id)
    # Keep the current api key while clearing session
    old_api_key = user_sessions.get(cid, {}).get("api_key")
    user_sessions[cid] = {
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}], 
        "total_tokens": 0,
        "api_key": old_api_key,
        "file_buffer": []
    }
    save_sessions()

def slide_window(session, threshold):
    """Sliding window: discard the oldest chat records when Token exceeds threshold"""
    while session["total_tokens"] > threshold and len(session["messages"]) >= 3:
        # 0 is system prompt
        # pop 1 twice to remove tha oldest user and assistant
        session["messages"].pop(1)
        session["messages"].pop(1)
        session["total_tokens"] -= 1000  # Rough deduction, exact value will be updated on next request