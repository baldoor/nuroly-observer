import os
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from .base import BaseProvider

class SlackProvider(BaseProvider):
    def __init__(self, core_callback):
        # Initialize with prefix from env or default '!'
        super().__init__("Slack", os.getenv("SLACK_PREFIX", "!"))
        self.token = os.getenv("SLACK_TOKEN")
        self.app_token = os.getenv("SLACK_APP_TOKEN")
        self.core_callback = core_callback
        
        self.client = AsyncApp(token=self.token)

    @staticmethod
    def is_configured():
        return bool(os.getenv("SLACK_TOKEN")) and bool(os.getenv("SLACK_APP_TOKEN"))

    async def start(self):
        @self.client.message("") 
        async def handle_message(message, say):
            chat_id = message['channel']
            text = message.get('text', "")
            user_id = message.get('user')
            
            # Forward the message to the core logic via callback
            await self.core_callback(self, chat_id, text, user_id)

        handler = AsyncSocketModeHandler(self.client, self.app_token)
        print(f"[✔] Slack Bot started (Prefix: {self.prefix})")
        await handler.start_async()

    async def send_message(self, chat_id, text):
        """Actual send function via the Slack API"""
        await self.client.client.chat_postMessage(channel=chat_id, text=text)