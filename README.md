# AI Telegram Assistant & Weather Bot

An asynchronous Telegram bot that integrates Google Gemini AI for natural conversation and provides real-time weather updates. Built with Python and Aiogram 3.

## Features
* **AI Integration:** Chat with Google Gemini 2.5 Flash model.
* **Weather Forecast:** Get real-time weather summaries for Kaiserslautern and Odessa via `wttr.in`.
* **Schedule System:** Automated morning weather digests using `APScheduler`.
* **Smart Formatting:** Auto-correction of Markdown parsing errors for stability.
* **Secure:** Credentials managed via environment variables.

## 🛠 Technology Stack
* Python 3.10+
* Aiogram 3 (Async Bot API)
* Google Generative AI SDK
* Aiohttp (Async HTTP requests)
* APScheduler
* Python-dotenv

## ⚙️ Installation & Setup

To run this bot on your own machine, follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/dIMONSTERIb/AiTelegramBot.git

cd AiTelegramBot
```

### 2. Set up Virtual Environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration

1. Rename `.env.example` to `.env`.

2. Open .env and insert your API keys:
- BOT_TOKEN: Get from `@BotFather` in Telegram.
- GEMINI_API_KEY: Get from Google AI Studio.
- MY_ADMIN_ID: Your numeric Telegram ID (for admin alerts,search via `@userinfobot` in Telegram ).

### 5. Run

```Bash
python TG_Bot.py
```

### 📜 Commands

- `/start` - Activate the bot menu.
- `/ai` - Enable AI chat mode.
- `/quit` - Disable AI chat mode.

### Note: This project demonstrates asynchronous programming, API integration, and task scheduling in Python.

### Preview
<div align="center">
  <img src="./Preview/Scr_1.jpg" width="45%" alt="Part 1" />
  <img src="./Preview/Scr_2.jpg" width="45%" alt="Part 2" />
</div>