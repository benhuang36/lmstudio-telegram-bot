# LM Studio Telegram Bot (Local LLM Bridge)

This is a Telegram bot project that connects to your local Large Language Model (via [LM Studio](https://lmstudio.ai/)).

> **📝 Introduction & Motivation** > This project is mainly built for practicing Python modular design and API integration. 
> By using Telegram's Long Polling method, you can safely chat with your home PC's AI from your phone anywhere—without opening router ports (Port Forwarding) or setting up HTTPS certificates.

## ✨ Key Features
* **MVC-like Architecture**: The code is separated into Controller, Service, and Model. It is very easy to read and update.
* **Hardware Protection (Thread Lock)**: A global lock makes sure only one request is sent to LM Studio at a time. This prevents the model from crashing under heavy load and will tell the user if the model is busy.
* **Sliding Window Memory**: It tracks the Token usage. When it gets close to the limit, it auto-deletes the oldest chat history to keep the conversation going smoothly.
* **Background "Typing" Indicator**: Uses a background thread and `with` statement to keep sending the "Typing..." status to Telegram while the model is thinking.
* **Response Time Tracking**: Auto-appends the exact thinking time (in seconds) to the final reply.

## 🛠️ Requirements
* **Python**: 3.8 or higher
* **LM Studio**: Local Server must be running (OpenAI API format compatible)
* **Python Packages**:
  * `pyTelegramBotAPI` (Handles Telegram Bot logic)
  * `requests` (Sends HTTP requests to the local API)

## 🤖 How to Create a Telegram Bot & Get IDs
If you are new to Telegram bots, follow these simple steps to get your keys:

**1. Get the Bot Token (`TELEGRAM_TOKEN`)**
* Open Telegram and search for `@BotFather`.
* Send the command `/newbot`.
* Follow the prompts to give your bot a name and a unique username (must end in `bot`).
* Once created, BotFather will give you an **HTTP API Token** (e.g., `123456789:ABCDefgh...`). Copy this token.

**2. Get your Chat ID (`ALLOWED_CHAT_IDS`)**
* Search for `@userinfobot` in Telegram.
* Send the command `/start` or just say hello.
* It will reply with your account details. Look for the `Id` (a sequence of numbers like `123456789`). Copy this number.

## 📂 Project Structure
```text
.
├── main.py                  # Entry point
├── config.py                # Global settings (API keys, Allowed IDs, etc.)
├── models/
│   └── session.py           # (Model) Manages chat memory and token count
├── services/
│   ├── llm_service.py       # (Service) Talks to LM Studio and manages the hardware lock
│   └── tg_utils.py          # (Service) Telegram tools (Typing thread and debug logs)
└── controllers/
    └── handlers.py          # (Controller) Handles Telegram commands and logic
```

## 🚀 How to Install and Run

**1. Clone the code**
```bash
git clone https://github.com/benhuang36/lmstudio-telegram-bot.git
cd lmstudio-telegram-bot
```

**2. Create a virtual environment (Recommended)**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install packages**
```bash
pip install pyTelegramBotAPI requests
```

**4. Setup Environment Variables**
Please create or open `config.py` (you can copy from `config.example.py` if available) and fill in your information:
* `TELEGRAM_TOKEN`: Your bot token from @BotFather.
* `ALLOWED_CHAT_IDS`: Your own Telegram User ID (numbers) to prevent strangers from using your PC's power.
* `LM_STUDIO_URL` & `LM_STUDIO_API_KEY`: The URL and API key from your LM Studio Local Server.

**5. Run the bot (Optional: using tmux for background running)**
```bash
tmux new -s tg_bot
python main.py
```
*(After you see "Bot started..." in the terminal, press `Ctrl+b` then `d` to leave it running in the background)*

## 💬 Telegram Commands
* **Text messages**: Chat directly with your local model.
* `/current_usage`: Check how many tokens and chat turns you have used so far.
* `/new_session`: Clear your chat memory and start a new conversation.

---
*Developed for learning and open-source sharing.*