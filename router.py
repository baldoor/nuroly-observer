import importlib
import os

class CommandRouter:
    def __init__(self):
        self.commands = {}
        # Mapping: Alias -> Filename in /commands
        self.mapping = {
            "p": "ping",
            "h": "help",
            "start": "help"
        }
        self.load_modules()

    def load_modules(self):
        cmd_path = os.path.join(os.path.dirname(__file__), 'commands')
        for file in os.listdir(cmd_path):
            if file.endswith(".py") and not file.startswith("__"):
                name = file[:-3]
                module = importlib.import_module(f"commands.{name}")
                self.commands[name] = module
                print(f"[*] Command '{name}' loaded.")

    def execute(self, alias, args):
        target = self.mapping.get(alias, alias)
        if target in self.commands:
            return self.commands[target].execute(args)
        return f"Unknown command: {alias}"