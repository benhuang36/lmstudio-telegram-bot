from config import SYSTEM_PROMPT

user_sessions = {}

def get_session(chat_id):
    """Get user session, initialize a clean state if it does not exist"""
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            # 💡 reserve system prompt
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}], 
            "total_tokens": 0
        }
    return user_sessions[chat_id]

def clear_session(chat_id):
    """Clear user chat history"""
    user_sessions[chat_id] = {
        # 💡 reserve system prompt
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}], 
        "total_tokens": 0
    }

def slide_window(session, threshold):
    """Sliding window: discard the oldest chat records when Token exceeds threshold"""
    while session["total_tokens"] > threshold and len(session["messages"]) >= 3:
        # 0 is system prompt
        # pop 1 twice to remove tha oldest user and assistant
        session["messages"].pop(1)
        session["messages"].pop(1)
        session["total_tokens"] -= 1000  # Rough deduction, exact value will be updated on next request