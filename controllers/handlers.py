import telebot
import telegramify_markdown
import time
import re
from config import ALLOWED_CHAT_IDS, MAX_TOKENS_THRESHOLD, ACTIVE_LLM, MAX_SINGLE_FILE_SIZE
from models.session import get_session, clear_session, slide_window, update_api_key, add_message, save_total_tokens, save_session
from services.llm_service import ask_llm, get_user_lock
from services.tg_utils import continuous_typing, split_text
from services.tg_utils import log_debug
import requests

bot_state = {
    "thinking_start_time": None
}

def register_handlers(bot):

    @bot.message_handler(commands=['set_api_key'])
    def handle_set_api_key(message):
        chat_id = message.chat.id
        if chat_id not in ALLOWED_CHAT_IDS: return
        
        parts = message.text.split(maxsplit=1)

        if len(parts) > 1:
            # With key
            new_key = parts[1].strip()
            validate_and_save_key(message, chat_id, new_key)
        else:
            msg = bot.reply_to(message, "🗝️ Please reply to this message with your API Key, or type `cancel` to abort:", parse_mode='Markdown')
            bot.register_next_step_handler(msg, receive_api_key_step)

    def receive_api_key_step(message):
        chat_id = message.chat.id
        if chat_id not in ALLOWED_CHAT_IDS: return
        
        new_key = message.text.strip()
        if new_key.lower() == "cancel":
            bot.send_message(chat_id, "🚫Setting API key is canceled.")
        else:
            validate_and_save_key(message, chat_id, new_key)

    def validate_and_save_key(message, chat_id, new_key):
        is_valid = True
        
        if ACTIVE_LLM == "openai" and not new_key.startswith("sk-"):
            is_valid = False
        elif ACTIVE_LLM == "gemini" and not new_key.startswith("AIza"):
            is_valid = False
        # LM Studio keys are flexible; no strict validation needed.

        if not is_valid:
            bot.reply_to(message, f"❌ Invalid API Key format for {ACTIVE_LLM}. Setting canceled.")
            return

        update_api_key(chat_id, new_key)
        try:
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, "✅ API Key updated and saved! (Your message was automatically deleted for security.)")
        except:
            bot.reply_to(message, "✅ API Key updated and saved! (Please manually delete your message containing the key for security.)")

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
        user_intent = message.text

        if session.get("file_buffer"):
            combined_prompt = "I have uploaded the following files:\n\n"
            for f in session["file_buffer"]:
                combined_prompt += f"--- File: {f['name']} ---\n{f['content']}\n\n"

            combined_prompt += f"--- User Intent ---\n{user_intent}"

            final_input = combined_prompt

            session["file_buffer"] = []
            save_session(chat_id, session)
        else:
            final_input = user_intent

        if not session.get("api_key"):
            bot.reply_to(
                message,
                "⚠️ Please set your API key first using the command:\n`/set_api_key YOUR_API_KEY`", 
                parse_mode='Markdown'
            )
            return

        # Request lock from Service layer
        user_lock = get_user_lock(chat_id)
        if not user_lock.acquire(blocking=False):
            # 💡 Read the start time of the current task, and calculate elapsed time
            start_t = bot_state.get("thinking_start_time")
            if start_t:
                elapsed = round(time.perf_counter() - start_t, 1)
                bot.reply_to(message, f"⏳ The model is thinking (for {elapsed}s). Please wait!")
            else:
                bot.reply_to(message, "⏳ The model is thinking. Please wait!")
            return

        try:
            session["messages"].append({"role": "user", "content": final_input})
            add_message(chat_id, "user", final_input)

            # ⏱️ Record start time and save to global state
            start_time = time.perf_counter() 
            bot_state["thinking_start_time"] = start_time

            with continuous_typing(bot, chat_id):
                # Call LLM Service
                reply_text, total_tokens = ask_llm(session["messages"], session.get("api_key"))

            # ⏱️ Calculate total elapsed time
            elapsed_time = round(time.perf_counter() - start_time, 1)

            # Update Model state
            session["messages"].append({"role": "assistant", "content": reply_text})
            add_message(chat_id, "assistant", reply_text)
            session["total_tokens"] = total_tokens
            slide_window(chat_id, MAX_TOKENS_THRESHOLD)

            save_total_tokens(chat_id, total_tokens)

            # Remove thought tag
            clean_text = re.sub(r'<thought>.*?</thought>', '', reply_text, flags=re.DOTALL)

            final_reply = f"{clean_text}\n\n_⏱️ Thinking time: {elapsed_time}s_"
            tg_safe_markdown = telegramify_markdown.markdownify(final_reply)
            message_chunks = split_text(tg_safe_markdown)

            # View: Send formatted message to user
            try:
                for chunk in message_chunks:
                    bot.reply_to(message, chunk, parse_mode='MarkdownV2')
            except telebot.apihelper.ApiTelegramException as e:
                log_debug(f"MarkdownV2 parsing failed: {str(e)}")
                log_debug(f"Failed content: {tg_safe_markdown}")
                plain_chunks = split_text(clean_text)
                for chunk in plain_chunks:
                    bot.reply_to(message, chunk)

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
            user_lock.release()

    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        chat_id = message.chat.id
        if chat_id not in ALLOWED_CHAT_IDS: return

        user_lock = get_user_lock(chat_id)
        if not user_lock.acquire(blocking=True):
            bot.reply_to(message, "⏳ Oops! System busy, please try again later!")
            return

        session = get_session(chat_id)
        file_name = message.document.file_name
        file_size = message.document.file_size
        max_size_in_kb = round(MAX_SINGLE_FILE_SIZE / 1024, 2)
        if file_size > MAX_SINGLE_FILE_SIZE:
            size_in_kb = round(file_size / 1024, 2)
            bot.reply_to(message, f"❌ Oops! That file is a bit too large. Please keep it under {max_size_in_kb}KB (Current size: {size_in_kb}KB)")
            return

        # 💡 check supported extension names.
        allowed_extensions = ('.c', '.kt', '.py', '.swift', '.h', '.sh', '.json', '.txt', '.md')
        if not file_name.lower().endswith(allowed_extensions):
            bot.reply_to(message, f"❌ Unsupported file type: {file_name}")
            return

        try:
            file_info = bot.get_file(message.document.file_id)
            log_debug(f"file_info.file_path: {file_info.file_path}")
            downloaded_file = bot.download_file(file_info.file_path)
            content = downloaded_file.decode('utf-8')
            log_debug(f"download file complete")

            # 💡 save file info in buffer
            session["file_buffer"].append({
                "name": file_name,
                "content": content
            })
            save_session(chat_id, session)

            bot.reply_to(message, f"📥 `{file_name}` added to buffer. (Total: {len(session['file_buffer'])} files)\nYou can send more files or type your instructions.")

        except Exception as e:
            bot.reply_to(message, f"❌ Failed to process file: {str(e)}")

        finally:
            user_lock.release()