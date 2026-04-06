import requests
import threading
from config import LM_STUDIO_URL, LM_STUDIO_API_KEY

# Global lock for hardware resource management
process_lock = threading.Lock()

def ask_llm(messages):
    """Send request to LM Studio and return (reply text, total tokens used)"""
    headers = {
        "Authorization": f"Bearer {LM_STUDIO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "local-model",
        "messages": messages,
        "temperature": 0.7
    }

    # Do not handle Exceptions here, let the Controller handle them
    response = requests.post(LM_STUDIO_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    reply_text = data['choices'][0]['message']['content']
    total_tokens = data.get('usage', {}).get('total_tokens', 0)
    
    return reply_text, total_tokens