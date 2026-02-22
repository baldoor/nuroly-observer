import os
import importlib

class CommandRouter:
    def __init__(self):
        self.commands = {}
        
        # Mapping: Alias -> Actual command name
        self.mapping = {
            "p": "ping",
            "h": "help",
            "start": "help"
        }
        
        # Load commands from both directories
        self._load_commands("commands")
        self._load_commands("custom_commands")

    def _load_commands(self, directory):
        # Skip if directory (e.g., custom_commands) does not exist
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
        # Resolve alias to actual command name (fallback to the command itself if no alias exists)
        target = self.mapping.get(command, command)
        
        if target in self.commands:
            try:
                return self.commands[target](args)
            except Exception as e:
                return f"Error executing '{target}': {str(e)}"
        return f"Unknown command: {command}. Type 'help' for available commands."