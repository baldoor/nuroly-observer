import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from .base import BaseProvider

class TelegramProvider(BaseProvider):
    def __init__(self, core_callback):
        # Initialize with name and prefix from environment
        super().__init__("Telegram", os.getenv("TELEGRAM_PREFIX", "/"))
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.core_callback = core_callback 
        self.app = None

    @staticmethod
    def is_configured():
        # Check if token exists and follows Telegram format
        token = os.getenv("TELEGRAM_TOKEN")
        return bool(token and ":" in token) 

    async def _handle_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Called by the library with every new message."""
        if not update.message or not update.message.text:
            return

        chat_id = update.message.chat_id
        text = update.message.text

        # Forward the message to main.py
        await self.core_callback(self, chat_id, text)

    async def send_message(self, chat_id, text):
        """Actual send function via the Telegram API."""
        if self.app:
            await self.app.bot.send_message(chat_id=chat_id, text=text)

    async def start(self):
        """Start the bot loop in a non-blocking way."""
        self.app = ApplicationBuilder().token(self.token).build()
        
        # Register handlers: Respond to all text messages and commands
        text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self._handle_update)
        cmd_handler = MessageHandler(filters.COMMAND, self._handle_update)
        
        self.app.add_handler(text_handler)
        self.app.add_handler(cmd_handler)

        # Initialize and start the application manually to avoid blocking
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

        print(f"[✔] Telegram Bot polling started (Prefix: {self.prefix})")
        
        # Keep the task alive so asyncio.gather doesn't finish immediately
        while True:
            await asyncio.sleep(3600)