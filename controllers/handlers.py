import telebot
import time
from config import ALLOWED_CHAT_IDS, MAX_TOKENS_THRESHOLD
from models.session import get_session, clear_session, slide_window
from services.llm_service import ask_llm, process_lock
from services.tg_utils import continuous_typing
from services.tg_utils import log_debug
import requests

bot_state = {
    "thinking_start_time": None
}

def register_handlers(bot):
    
    @bot.message_handler(commands=['new_session'])
    def handle_new_session(message):
        chat_id = message.chat.id
        if chat_id not in ALLOWED_CHAT_IDS: return
        clear_session(chat_id)
        bot.reply_to(message, "✅ Chat memory cleared! The new session has started.")

    @bot.message_handler(commands=['current_usage'])
    def handle_current_usage(message):
        chat_id = message.chat.id
        if chat_id not in ALLOWED_CHAT_IDS: return
        session = get_session(chat_id)
        tokens = session.get("total_tokens", 0)
        msg = (f"📊 Token usage: {tokens} / {MAX_TOKENS_THRESHOLD}\n"
               f"📜 Chat history: {len(session['messages']) // 2} turns")
        bot.reply_to(message, msg)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        chat_id = message.chat.id
        if chat_id not in ALLOWED_CHAT_IDS:
            bot.reply_to(message, "Access denied. You don't have permission.")
            return

        session = get_session(chat_id)

        # Request lock from Service layer
        if not process_lock.acquire(blocking=False):
            # 💡 Read the start time of the current task, and calculate elapsed time
            start_t = bot_state.get("thinking_start_time")
            if start_t:
                elapsed = round(time.perf_counter() - start_t, 1)
                bot.reply_to(message, f"⏳ The model is thinking (for {elapsed}s). Please wait!")
            else:
                bot.reply_to(message, "⏳ The model is thinking. Please wait!")
            return

        try:
            session["messages"].append({"role": "user", "content": message.text})

            # ⏱️ Record start time and save to global state
            start_time = time.perf_counter() 
            bot_state["thinking_start_time"] = start_time

            with continuous_typing(bot, chat_id):
                # Call LLM Service
                reply_text, total_tokens = ask_llm(session["messages"])

            # ⏱️ Calculate total elapsed time
            elapsed_time = round(time.perf_counter() - start_time, 1)

            # Update Model state
            session["messages"].append({"role": "assistant", "content": reply_text})
            session["total_tokens"] = total_tokens
            slide_window(session, MAX_TOKENS_THRESHOLD)

            final_reply = f"{reply_text}\n\n_⏱️ Thinking time: {elapsed_time}s_"

            # View: Send formatted message to user
            try:
                bot.reply_to(message, final_reply, parse_mode='Markdown')
            except telebot.apihelper.ApiTelegramException as e:
                log_debug(f"Markdown parsing failed: {str(e)}")
                bot.reply_to(message, reply_text)

        except requests.exceptions.ConnectionError as e:
            log_debug(f"Connection error: {str(e)}")
            bot.reply_to(message, "Cannot connect to LM Studio. Is the server running?")
            if session["messages"] and session["messages"][-1]["role"] == "user":
                session["messages"].pop()

        except Exception as e:
            log_debug(f"Unexpected error: {str(e)}")
            bot.reply_to(message, f"An error occurred: {str(e)}")
            if session["messages"] and session["messages"][-1]["role"] == "user":
                session["messages"].pop()

        finally:
            bot_state["thinking_start_time"] = None
            process_lock.release()