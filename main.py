# main.py
import telebot
from config import TELEGRAM_TOKEN
from controllers.handlers import register_handlers

def main():
    print("Initializing Telegram Bot...")
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    
    print("Registering routes and Controllers...")
    register_handlers(bot)
    
    print("Bot started, beginning Long Polling!")
    bot.infinity_polling()

if __name__ == '__main__':
    main()