# Telegram to Immich Bot

Created by Mel

Inspired by https://github.com/myanesp/telegram-immich-bot/

## Why?

This Docker container provides a simple way to automatically upload files from Telegram to your Immich photo management system. It's perfect for:

- Images, photos and videos sent without compression that your relatives send you via Telegram
- Automatically backing up photos/videos sent to a Telegram bot
- Creating a simple upload pipeline for your personal media

## Features

- ✅ Automatic file uploads from Telegram to Immich
- ✅ Preserves original file metadata (for assets sent as Documents)
- ✅ User restriction control (only allow specific Telegram user IDs)
- ✅ Simple configuration via environment variables

## How to Run

1. **Set up your Telegram bot**:
   - Create a new bot using [@BotFather](https://t.me/BotFather)
   - Note down your bot token
   - Start a chat with your new bot

2. **Configure your Immich instance**:
   - Ensure your Immich API is accessible from the host
   - Generate an API key from your Immich settings

3. **Create a container**

```bash
cd ./telegram-immich-bot
docker build -t telegram-immich-bot .
```

4. **Configure your environment with docker-compose.yml**

5. **Start the container**

```bash
docker compose up -d
```

6. **Send a file to your bot**


## Environment Variables

| VARIABLE | MANDATORY | DESCRIPTION | DEFAULT |
|----------|:---------:|-------------------------------------------------------------|---------|
| TELEGRAM_BOT_TOKEN | ✅ | Your Telegram bot token obtained from @BotFather | - |
| IMMICH_API_URL | ✅ | Full URL to your Immich API endpoint (can be local or public) (e.g., `http://your-immich-instance:2283/api`) | - |
| IMMICH_API_KEY | ✅ | API key for authenticating with your Immich instance | - |
| ALLOWED_USER_IDS | ✅ | Comma-separated list of Telegram user IDs allowed to use the bot (e.g., `123456789,987654321`) | - |
| UPLOAD_TIMEZONE | - | Time zone to be set for an asset after upload | Europe/Moscow |
