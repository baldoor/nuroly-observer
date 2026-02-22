import os
from dotenv import load_dotenv
from router import CommandRouter
from providers.telegram import TelegramProvider

load_dotenv()

class ModuBot:
    def __init__(self):
        self.router = CommandRouter()
        self.providers = []
        
        # Load authorized users from environment
        raw_allowed = os.getenv("TELEGRAM_ALLOWED_USERS", "")
        self.tg_whitelist = [int(i.strip()) for i in raw_allowed.split(",") if i.strip()]
        
        print(f"[*] Security: {len(self.tg_whitelist)} users whitelisted for Telegram.")

    async def handle_incoming(self, provider, chat_id, text):
        # SPECIFIC CHECK FOR TELEGRAM
        if isinstance(provider, TelegramProvider):
            if self.tg_whitelist and chat_id not in self.tg_whitelist:
                print(f"[!] Access denied for Telegram ID: {chat_id}")
                # Optional: await provider.send_message(chat_id, "No access.")
                return

        if provider.is_command(text):
            cmd = provider.extract_command(text)
            args = text.split()[1:]
            response = self.router.execute(cmd, args)
            await provider.send_message(chat_id, response)

    def run(self):
        if TelegramProvider.is_configured():
            # Important: We pass the handle_incoming method as a callback
            tg = TelegramProvider(self.handle_incoming)
            self.providers.append(tg)
            tg.start()
        else:
            print("[!] Telegram Provider nicht bereit. Key in .env prüfen.")

if __name__ == "__main__":
    bot = ModuBot()
    bot.run()