# config.py

DEBUG = False

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'
ALLOWED_CHAT_IDS = [123456789]

# Available options: "lm_studio", "openai", or "gemini"
ACTIVE_LLM = "lm_studio"

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
LM_STUDIO_API_KEY = "YOUR_API_KEY_HERE"
LM_STUDIO_MODEL = "local-model"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = "sk-proj-YOUR_OPENAI_API_KEY_HERE"
# Common models: "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"
OPENAI_MODEL = "gpt-4o-mini"

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
# Common models: "gemini-2.5-flash", "gemini-2.5-pro"
GEMINI_MODEL = "gemini-2.5-flash"

MAX_TOKENS_THRESHOLD = 13000
