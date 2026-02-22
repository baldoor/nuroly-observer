# Telegram Setup Guide

Setting up a Telegram bot is very straightforward. You manage everything through Telegram's official "BotFather".

## Step 1: Create the Bot
1. Open your Telegram app and search for the user **@BotFather**.
2. Start a chat and send the command `/newbot`.
3. BotFather will ask for a **Name** (e.g., `My ChatOp Bot`) and a **Username** (must end in `bot`, e.g., `chatop_bot`).
4. Once created, BotFather will give you an **HTTP API Token** (looks like `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`). 
5. Paste this token into your `.env` file as `TELEGRAM_TOKEN`.

## Step 2: Get your Telegram User ID (For Whitelisting)
To make your bot secure, you need your personal User ID.
1. Search for **@userinfobot** (or any similar ID-bot) in Telegram.
2. Start a chat with it.
3. It will reply with your numeric ID (e.g., `123456789`).
4. Paste this number into your `.env` file as `TELEGRAM_ALLOWED_USERS`.

## Step 3: Start Chatting
Send your first message (like `/help` or `/ping`) to your new bot!