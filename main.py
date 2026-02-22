import os
import asyncio  # Required for gather and running the loop
from dotenv import load_dotenv
from router import CommandRouter
from providers.telegram import TelegramProvider
from providers.slack import SlackProvider  # Don't forget to import Slack

load_dotenv()

class ModuBot:
    def __init__(self):
        self.router = CommandRouter()
        self.providers = []
        
        # Load Telegram whitelist
        raw_allowed = os.getenv("TELEGRAM_ALLOWED_USERS", "")
        self.tg_whitelist = [int(i.strip()) for i in raw_allowed.split(",") if i.strip()]
        
        # Load Slack whitelist (Slack IDs are strings, so no int() casting)
        raw_slack = os.getenv("SLACK_ALLOWED_USERS", "")
        self.slack_whitelist = [i.strip() for i in raw_slack.split(",") if i.strip()]
        
        print(f"[*] Security: {len(self.tg_whitelist)} users whitelisted for Telegram.")
        print(f"[*] Security: {len(self.slack_whitelist)} users whitelisted for Slack.")

    async def handle_incoming(self, provider, chat_id, text, sender_id=None):
        # Specific check for Telegram
        if isinstance(provider, TelegramProvider):
            if self.tg_whitelist and sender_id not in self.tg_whitelist:
                print(f"[!] Access denied for Telegram User: {sender_id} in Chat: {chat_id}")
                return

        # Specific check for Slack
        if isinstance(provider, SlackProvider):
            if self.slack_whitelist and sender_id not in self.slack_whitelist:
                print(f"[!] Access denied for Slack User: {sender_id}")
                return

        if provider.is_command(text):
            cmd = provider.extract_command(text)
            args = text.split()[1:]
            response = self.router.execute(cmd, args)
            await provider.send_message(chat_id, response)

    async def run(self):
        tasks = []
        
        # Telegram Start-Check
        if TelegramProvider.is_configured():
            tg = TelegramProvider(self.handle_incoming)
            self.providers.append(tg)
            # Ensure telegram.py:start() is now 'async def start(self):'
            tasks.append(tg.start())
        
        # Slack Start-Check
        if SlackProvider.is_configured():
            sl = SlackProvider(self.handle_incoming)
            self.providers.append(sl)
            tasks.append(sl.start())

        if not tasks:
            print("[!] No providers configured. Please check your .env file.")
            return

        # Start all configured providers in parallel
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    bot = ModuBot()
    # Correct way to start the async entry point
    asyncio.run(bot.run())