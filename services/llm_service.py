import requests
import threading
from config import (
    ACTIVE_LLM,
    LM_STUDIO_URL, LM_STUDIO_API_KEY, LM_STUDIO_MODEL,
    OPENAI_URL, OPENAI_API_KEY, OPENAI_MODEL,
    GEMINI_URL, GEMINI_API_KEY, GEMINI_MODEL
)

# Global lock for hardware resource management
process_lock = threading.Lock()

def ask_llm(messages):
    """Send request to the active LLM backend and return (reply text, total tokens used)"""

    # Check config to determine which backend to use
    if ACTIVE_LLM == "openai":
        api_url = OPENAI_URL
        api_key = OPENAI_API_KEY
        model_name = OPENAI_MODEL
    elif ACTIVE_LLM == "gemini":
        api_url = GEMINI_URL
        api_key = GEMINI_API_KEY
        model_name = GEMINI_MODEL
    else:
        api_url = LM_STUDIO_URL
        api_key = LM_STUDIO_API_KEY
        model_name = LM_STUDIO_MODEL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7
    }

    # Do not handle Exceptions here, let the Controller handle them
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
