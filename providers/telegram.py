import os
import asyncio
from telegram import Update, BotCommand
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
        user_id = update.message.from_user.id

        # Forward the message to main.py including the user_id
        await self.core_callback(self, chat_id, text, user_id)
        
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
        
        # Dynamically set bot commands menu from router
        await self._set_bot_commands()
        
        await self.app.start()
        await self.app.updater.start_polling()

        print(f"[✔] Telegram Bot polling started (Prefix: {self.prefix})")
        print(f"[✔] Bot command menu updated with {len(self.app.bot_data.get('commands', []))} commands")
        
        # Keep the task alive so asyncio.gather doesn't finish immediately
        while True:
            await asyncio.sleep(3600)
    
    async def _set_bot_commands(self):
        """Dynamically generate and set Telegram bot command menu from available commands."""
        try:
            from router import CommandRouter
            router = CommandRouter()
            
            bot_commands = []
            for cmd_name in sorted(router.commands.keys()):
                module = router.commands[cmd_name]
                # Get description (fallback to docstring or generic text)
                description = getattr(module, 'description', None)
                if not description and hasattr(module, 'execute') and module.execute.__doc__:
                    description = module.execute.__doc__.strip().split('\n')[0]
                if not description:
                    description = f"Execute {cmd_name} command"
                
                # Telegram command descriptions have a 256 character limit
                description = description[:256]
                bot_commands.append(BotCommand(cmd_name, description))
            
            # Set commands in Telegram
            await self.app.bot.set_my_commands(bot_commands)
            self.app.bot_data['commands'] = bot_commands
            
            print(f"[*] Telegram: Registered {len(bot_commands)} commands in bot menu")
        except Exception as e:
            print(f"[!] Failed to set Telegram bot commands: {e}")