import os
from slack_bolt.async_app import AsyncApp  # Hier AsyncApp verwenden!
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler  # Der korrekte Pfad!
from .base import BaseProvider

class SlackProvider(BaseProvider):
    def __init__(self, core_callback):
        # Initialize with prefix from env or default '!'
        super().__init__("Slack", os.getenv("SLACK_PREFIX", "!"))
        self.token = os.getenv("SLACK_TOKEN")
        self.app_token = os.getenv("SLACK_APP_TOKEN")
        self.core_callback = core_callback
        
        # Nutze AsyncApp anstelle von App
        self.client = AsyncApp(token=self.token)

    @staticmethod
    def is_configured():
        # Check if both required tokens are present
        return bool(os.getenv("SLACK_TOKEN")) and bool(os.getenv("SLACK_APP_TOKEN"))

    async def start(self):
        # Register event handler for all incoming messages
        @self.client.message("") 
        async def handle_message(message, say):
            chat_id = message['channel']
            text = message.get('text', "")
            # Forward the message to the core logic via callback
            await self.core_callback(self, chat_id, text)

        handler = AsyncSocketModeHandler(self.client, self.app_token)
        print(f"[✔] Slack Bot started (Prefix: {self.prefix})")
        await handler.start_async()

    async def send_message(self, chat_id, text):
        """Actual send function via the Slack API"""
        await self.client.client.chat_postMessage(channel=chat_id, text=text)