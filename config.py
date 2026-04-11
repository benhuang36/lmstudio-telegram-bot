import os
from dotenv import load_dotenv

load_dotenv()

APP_VERSION = os.getenv("APP_VERSION", "unknown")

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
allowed_ids_str = os.getenv("ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS = [int(x.strip()) for x in allowed_ids_str.split(",") if x.strip()]

ACTIVE_LLM = os.getenv("ACTIVE_LLM", "lm_studio")
MAX_TOKENS_THRESHOLD = int(os.getenv("MAX_TOKENS_THRESHOLD", "13000"))
MAX_SINGLE_FILE_SIZE = int(os.getenv("MAX_SINGLE_FILE_SIZE", "1048576"))

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")

GEMINI_URL = os.getenv("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemma-4-31b-it")

OPENAI_URL = os.getenv("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

default_prompt = "You are a helpful AI assistant."
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", default_prompt).replace("\\n", "\n")
