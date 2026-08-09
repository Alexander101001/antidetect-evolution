#!/bin/bash
# Run easy Telegram bot 24/7
cd /data/data/com.termux/files/home/.pi/skills/antidetect-stack

while true; do
    python3 telegram_easy/easy_telegram_bot.py 2>&1
    echo "Bot crashed. Restarting in 10s..."
    sleep 10
done
