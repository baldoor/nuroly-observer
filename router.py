import importlib
import os
import sys
import logging

class CommandRouter:
    def __init__(self):
        self.commands = {}
        self.mapping = {}  # Automatically loaded from command modules
        self.load_commands()

    def load_commands(self):
        """
        Dynamically loads all .py files from the commands/ directory.
        Commands can optionally define an 'aliases' list for shortcuts.
        """
        self.commands.clear()
        self.mapping.clear()
        
        # Path to the commands directory
        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        
        if not os.path.exists(commands_dir):
            os.makedirs(commands_dir)
            return

        for filename in os.listdir(commands_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    full_module_path = f"commands.{module_name}"
                    
                    # If the module was already loaded, force a reload
                    if full_module_path in sys.modules:
                        module = importlib.reload(sys.modules[full_module_path])
                    else:
                        module = importlib.import_module(full_module_path)
                    
                    if hasattr(module, "execute"):
                        self.commands[module_name] = module
                        logging.info(f"[*] Loaded command: {module_name}")
                        
                        # Load aliases from the command module
                        if hasattr(module, "aliases"):
                            for alias in module.aliases:
                                self.mapping[alias] = module_name
                                logging.info(f"[*]   └─ Alias: {alias} -> {module_name}")
                except Exception as e:
                    logging.error(f"[!] Failed to load command {module_name}: {e}")

    def execute(self, command_name, args):
        """
        Finds and executes the command. Fixes the AttributeError from main.py.
        """
        # Check for aliases (e.g. 'p' -> 'ping')
        target = self.mapping.get(command_name, command_name)
        
        if target in self.commands:
            try:
                return self.commands[target].execute(args)
            except Exception as e:
                logging.error(f"Error executing {target}: {e}")
                return f"⚠️ Error in command '{target}': {str(e)}"
        
        return f"Unknown command: {command_name}"