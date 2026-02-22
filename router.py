import os
import importlib

class CommandRouter:
    def __init__(self):
        self.commands = {}
        # Wir laden Befehle aus beiden Ordnern
        self._load_commands("commands")
        self._load_commands("custom_commands")

    def _load_commands(self, directory):
        # Wenn der Ordner (z.B. custom_commands) nicht existiert, überspringen wir ihn einfach
        if not os.path.exists(directory):
            return

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                command_name = filename[:-3]
                module_path = f"{directory}.{command_name}"
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "execute"):
                        self.commands[command_name] = module.execute
                        print(f"[*] Command '{command_name}' loaded from {directory}.")
                except Exception as e:
                    print(f"[!] Failed to load command '{command_name}': {e}")

    def execute(self, command, args):
        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"Error executing '{command}': {str(e)}"
        return f"Unknown command: {command}. Type 'help' for available commands."