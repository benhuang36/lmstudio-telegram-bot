# main.py
import telebot
from config import TELEGRAM_TOKEN
from controllers.handlers import register_handlers
from services.llm_service import get_active_model_info

def main():
    print("Initializing Telegram Bot...")
    bot = telebot.TeleBot(TELEGRAM_TOKEN)

    print("Registering routes and Controllers...")
    register_handlers(bot)

    backend, model_name = get_active_model_info()
    print(f"Bot started, beginning Long Polling! (Backend: {backend} | Model: {model_name})")

    bot.infinity_polling()

if __name__ == '__main__':
    main()
