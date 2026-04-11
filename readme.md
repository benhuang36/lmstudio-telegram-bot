# Telegram LLM Bridge (LM Studio / OpenAI / Gemini)

This is a Telegram bot project that connects your phone to Large Language Models. It supports local LLMs (via [LM Studio](https://lmstudio.ai/)) and cloud models like OpenAI and Gemini.

> **📝 Introduction & Motivation** > This project is mainly built for practicing Python modular design and API integration. 
> By using Telegram's Long Polling method, you can safely chat with AI from your phone anywhere.

## ✨ Key Features
* **Bring Your Own Key (BYOK)**: For security, there are no hardcoded keys. Users must set their own API key via Telegram commands.
* **Persistent Memory**: Chat history and API keys are securely stored in a local SQLite database, ensuring your conversations are preserved even after bot restarts.
* **Multi-Backend Support**: Switch between local compute (LM Studio) and cloud APIs (OpenAI, Gemini) easily in the `.env` file.
* **Sliding Window Memory**: Auto-deletes the oldest chat history to keep the conversation going smoothly when tokens reach the limit.
* **Safe Markdown**: Uses `telegramify_markdown` to completely prevent Telegram formatting errors.
* **Background "Typing" Indicator**: Keeps sending the "Typing..." status to Telegram while the model is thinking.
* **File-to-Context Support**: Upload source code or text files (e.g., .py, .swift, .md) to provide context. The bot buffers these files and combines them with your final prompt for a comprehensive answer.

## 🛠️ Requirements
* **Python**: 3.8 or higher
* **Python Packages**:
  * `pyTelegramBotAPI` (Handles Telegram Bot logic)
  * `requests` (Sends HTTP requests to the APIs)
  * `python-dotenv` (Loads `.env` variables safely)
  * `telegramify_markdown` (Ensures safe text formatting)

## 🤖 How to Create a Telegram Bot & Get IDs
**1. Get the Bot Token (`TELEGRAM_TOKEN`)**
* Open Telegram and search for `@BotFather`.
* Send `/newbot` and follow the prompts.
* Copy the **HTTP API Token** (e.g., `123456789:ABCDefgh...`).

**2. Get your Chat ID (`ALLOWED_CHAT_IDS`)**
* Search for `@userinfobot` in Telegram and send `/start`.
* Copy your `Id` (a sequence of numbers like `123456789`).

## 📂 Project Structure
```text
.
├── main.py                  # Entry point
├── config.py                # Loads settings from .env safely
├── .env.example             # Example environment variables
├── data/
│   └── sessions.db          # (Auto-generated) SQLite database for user memory and API keys
├── models/
│   └── session.py           # Manages chat memory and JSON local storage
├── services/
│   ├── llm_service.py       # Routes requests to LM Studio/OpenAI/Gemini
│   └── tg_utils.py          # Telegram tools (Typing thread and debug logs)
└── controllers/
    └── handlers.py          # Handles Telegram commands and logic
```

## 🚀 How to Install and Run

### Option 1: Native Installation
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
pip install pyTelegramBotAPI requests python-dotenv telegramify_markdown
```

**4. Setup Environment Variables**
Copy the example config file:
```bash
cp .env.example .env
```
Open the `.env` file and fill in your `TELEGRAM_TOKEN` and `ALLOWED_CHAT_IDS`. You can also choose your default `ACTIVE_LLM` here.

**5. Run the bot (using tmux for background running)**
```bash
tmux new -s tg_bot
python main.py
```
*(After you see the startup log, press `Ctrl+b` then `d` to leave it running in the background)*

### Option 2: Docker Deployment (Recommended)
**1. Prepare `.env`**
``` bash
cp .env.example .env
# Update your TELEGRAM_TOKEN and ALLOWED_CHAT_IDS in .env
```

**2. Start the bot:**
``` bash
docker compose up -d
```

**3. Check logs:**
``` bash
docker compose logs -f
```

## 💬 Telegram Commands
The command menu will automatically show up in Telegram. 
* `/set_api_key YOUR_KEY`: **(Required)** Set your personal API key before you start chatting.
* `/new_session`: Clear your chat memory and start a new conversation.
* `/current_usage`: Check token usage and chat turns.

## 📂 File Upload Support
You can send files directly to the bot to let the AI analyze your code or documents:
1. **Upload Files**: Send one or more supported files (`.c`, `.kt`, `.py`, `.swift`, `.h`, `.sh`, `.json`, `.txt`, `.md`).
2. **Context Buffering**: The bot will store these files in a temporary buffer.
3. **Ask Questions**: Once you send a text message, the bot will combine all buffered files with your question and send them to the AI.
4. **Automatic Clear**: The buffer is automatically cleared after each AI response.

*Note: To ensure stability, there is a maximum file size limit defined by `MAX_SINGLE_FILE_SIZE` in the `.env` file.*

## ⚙️ Environment Variables `(.env)`
|Variable|Description|
|----|----|
|APP_VERSION|Current version of the app (used for Docker tagging).|
|TELEGRAM_TOKEN|Your Bot Token from @BotFather.|
|ALLOWED_CHAT_IDS|Comma-separated list of allowed Telegram User IDs.|
|ACTIVE_LLM|Choose between gemini, openai, or lm_studio.|
| MAX_SINGLE_FILE_SIZE | Maximum allowed size for a single uploaded file (in bytes). e.g., `1048576` for 1MB. |
|SYSTEM_PROMPT|The initial instruction for the AI's personality.|

## 💾 Data Persistence
The project automatically creates a `data/` directory. When running via Docker, this directory is mounted as a volume. By using SQLite, this ensures your API keys and Chat History remain safe and consistent during updates or container restarts.

---
*Developed for learning and open-source sharing.*