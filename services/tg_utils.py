import threading
from contextlib import contextmanager
from config import DEBUG

def log_debug(msg):
    """Debug log function, controlled by config.DEBUG"""
    if DEBUG:
        print(f"[Debug] {msg}")

@contextmanager
def continuous_typing(bot, chat_id):
    stop_typing = threading.Event()

    def keep_typing():
        log_debug(f"🚀 Background typing thread started (chat_id: {chat_id})")
        while not stop_typing.is_set():
            try:
                log_debug("📡 Sending typing status to Telegram...")
                bot.send_chat_action(chat_id, 'typing')
                log_debug("✅ Typing status sent successfully")
            except Exception as e: # Catch exception to prevent thread crash
                print(f"[Debug] ❌ Typing status failed: {e}")
            stop_typing.wait(4)

        log_debug("🛑 Background typing thread closed safely")

    typing_thread = threading.Thread(target=keep_typing)
    typing_thread.start()

    try:
        yield 
    finally:
        stop_typing.set()
        typing_thread.join()