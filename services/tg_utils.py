import threading
from contextlib import contextmanager
from config import DEBUG, TELEGRAM_MAX_MESSAGE_LEN

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

def split_text(text, limit=4096):
    """Split long text into smaller chunks, preserving line breaks as much as possible."""
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = []
    current_length = 0

    # Split by newline characters to avoid breaking paragraphs
    paragraphs = text.split('\n')

    for para in paragraphs:
        # +1 to account for the newline character removed by split()
        para_len = len(para) + 1

        if current_length + para_len > limit:
            # If adding the current paragraph exceeds the limit,
            # package the previous content into a chunk
            chunks.append('\n'.join(current_chunk))
            current_chunk = [para]
            current_length = para_len
        else:
            current_chunk.append(para)
            current_length += para_len

    # Append the remaining part
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    # Special handling: If a single paragraph exceeds the limit
    # (e.g., an extremely long line of code), we must force a hard split
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > limit:
            # Force split the oversized chunk
            for i in range(0, len(chunk), limit):
                final_chunks.append(chunk[i:i+limit])
        else:
            final_chunks.append(chunk)

    return final_chunks