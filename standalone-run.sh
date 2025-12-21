#!/bin/bash

export TELEGRAM_BOT_TOKEN=xxx:xxxxx
export IMMICH_API_KEY=xxxxxxxxxx
export IMMICH_API_URL=https://your-immich/api
export ALLOWED_USER_IDS=123456789
export UPLOAD_TIMEZONE=Europe/Moscow

python3 ./app/bot.py
