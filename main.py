import telebot
from telebot.types import BotCommand
from config import APP_VERSION, TELEGRAM_TOKEN
from controllers.handlers import register_handlers
from services.llm_service import get_active_model_info

def setup_menu(bot):
    """Set up the Telegram command menu"""
    bot.set_my_commands([
        BotCommand("new_session", "✨ Clear memory and start a new conversation"),
        BotCommand("current_usage", "📊 Check token usage and memory turns"),
        BotCommand("set_api_key", "🗝️ Set your personal API key")
    ])
    print("Command menu has been successfully set up!")

def main():
    print(f"🚀 Initializing Telegram Bot v{APP_VERSION}")

    bot = telebot.TeleBot(TELEGRAM_TOKEN)

    setup_menu(bot)

    print("Registering routes and Controllers...")
    register_handlers(bot)

    backend, model_name = get_active_model_info()
    print(f"Bot started, beginning Long Polling! (Backend: {backend} | Model: {model_name})")

    bot.infinity_polling()

if __name__ == '__main__':
    main()
