import os
import asyncio  # Required for gather and running the loop
import math
from dotenv import load_dotenv
from router import CommandRouter
from providers.telegram import TelegramProvider
from providers.slack import SlackProvider  # Don't forget to import Slack
from rate_limiting import RateLimiter  # Rate limiting support

load_dotenv()

class ModuBot:
    def __init__(self):
        # Enable debug mode if DEBUG=true in .env
        debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        self.router = CommandRouter(debug_mode=debug_mode)
        self.providers = []
        
        # Initialize rate limiter
        rate_limit_max = int(os.getenv("RATE_LIMIT_MAX_TOKENS", "10"))
        rate_limit_per_min = int(os.getenv("RATE_LIMIT_TOKENS_PER_MINUTE", "10"))
        self.rate_limiter = RateLimiter(
            max_tokens=rate_limit_max,
            tokens_per_minute=rate_limit_per_min
        )
        
        # Load Telegram whitelist
        raw_allowed = os.getenv("TELEGRAM_ALLOWED_USERS", "")
        self.tg_whitelist = [int(i.strip()) for i in raw_allowed.split(",") if i.strip()]
        
        # Load Slack whitelist (Slack IDs are strings, so no int() casting)
        raw_slack = os.getenv("SLACK_ALLOWED_USERS", "")
        self.slack_whitelist = [i.strip() for i in raw_slack.split(",") if i.strip()]
        
        print(f"[*] Security: {len(self.tg_whitelist)} users whitelisted for Telegram.")
        print(f"[*] Security: {len(self.slack_whitelist)} users whitelisted for Slack.")
        print(f"[*] Rate Limiting: {rate_limit_max} commands per burst, {rate_limit_per_min} per minute")

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

        # Rate limiting check
        if sender_id:
            # Create unique key per provider and user
            user_key = f"{provider.__class__.__name__}_{sender_id}"
            limit_check = self.rate_limiter.check_limit(user_key)
            
            if not limit_check.allowed:
                wait_seconds = math.ceil(limit_check.wait_time)
                print(f"[!] Rate limit exceeded for {user_key}")
                await provider.send_message(
                    chat_id,
                    f"⏱️ Rate limit exceeded! Please wait {wait_seconds} seconds before sending another command."
                )
                return

        if provider.is_command(text):
            cmd = provider.extract_command(text)
            args = text.split()[1:]
            response = await self.router.execute(cmd, args)
            await provider.send_message(chat_id, response)

    async def run(self):
        print(r"""
 _   _                   _          ___   _                                
| \ | | _   _  _ __ ___ | | _   _  / _ \ | |__  ___   ___  _ __ __   __ ___ _ __ 
|  \| || | | || '__/ _ \| || | | || | | || '_ \/ __| / _ \| '__|\ \ / // _ \ '__|
| |\  || |_| || | | (_) | || |_| || |_| || |_) \__ \|  __/| |    \ V /|  __/ |   
|_| \_| \__,_||_|  \___/|_| \__, | \___/ |_.__/|___/ \___||_|     \_/  \___|_|   
                            |___/                                                
        """)
        print("[*] Initializing Nuroly-Observer Systems...")
        print(f"[*] Security: {len(self.tg_whitelist)} users whitelisted for Telegram.")
        print(f"[*] Security: {len(self.slack_whitelist)} users whitelisted for Slack.")

        tasks = []

        if TelegramProvider.is_configured():
            tg = TelegramProvider(self.handle_incoming)
            self.providers.append(tg)
            tasks.append(tg.start())

        if SlackProvider.is_configured():
            sl = SlackProvider(self.handle_incoming)
            self.providers.append(sl)
            tasks.append(sl.start())

        if tasks:
            print("[*] All configured providers are starting up...")
            await asyncio.gather(*tasks)
        else:
            print("[!] Critical Error: No providers (Telegram/Slack) configured. Check your .env file!")


if __name__ == "__main__":
    bot = ModuBot()
    # Correct way to start the async entry point
    asyncio.run(bot.run())