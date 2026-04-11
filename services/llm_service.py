import requests
import threading
from config import (
    ACTIVE_LLM,
    LM_STUDIO_URL, LM_STUDIO_MODEL,
    OPENAI_URL, OPENAI_MODEL,
    GEMINI_URL, GEMINI_MODEL
)

user_locks = {}
manager_lock = threading.Lock()

def get_user_lock(chat_id):
    with manager_lock:
        if chat_id not in user_locks:
            user_locks[chat_id] = threading.Lock()
        return user_locks[chat_id]

def ask_llm(messages, user_api_key):
    """Send request to the active LLM backend using the user's personal API key"""

    if ACTIVE_LLM == "openai":
        api_url = OPENAI_URL
        model_name = OPENAI_MODEL
    elif ACTIVE_LLM == "gemini":
        api_url = GEMINI_URL
        model_name = GEMINI_MODEL
    else:
        api_url = LM_STUDIO_URL
        model_name = LM_STUDIO_MODEL

    headers = {
        "Authorization": f"Bearer {user_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    reply_text = data['choices'][0]['message']['content']
    total_tokens = data.get('usage', {}).get('total_tokens', 0)

    return reply_text, total_tokens

def get_active_model_info():
    """Return the current active backend and model name for logging"""
    if ACTIVE_LLM == "openai":
        return "OpenAI", OPENAI_MODEL
    elif ACTIVE_LLM == "gemini":
        return "Gemini", GEMINI_MODEL
    else:
        return "LM Studio", LM_STUDIO_MODEL