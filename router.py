import importlib
import os
import sys
import logging
import traceback
import asyncio
import time
from typing import Dict, List, Optional

# Import custom exceptions and config
try:
    from exceptions import CommandTimeoutError
    from config import Config
except ImportError:
    # Fallback if not available
    class CommandTimeoutError(Exception):
        pass
    
    class Config:
        DEFAULT_COMMAND_TIMEOUT = 30
        
        @staticmethod
        def get_command_timeout(command_name: str) -> int:
            return 30

# Get logger instance
logger = logging.getLogger(__name__)


class CommandRouter:
    def __init__(self, debug_mode: bool = False):
        self.commands: Dict[str, object] = {}
        self.mapping: Dict[str, str] = {}  # Alias -> Command mapping
        self.failed_commands: List[str] = []  # Track failed command loads
        self.debug_mode = debug_mode
        self.execution_stats = {
            "success": 0,
            "failed": 0,
            "timeout": 0,
            "total_execution_time": 0.0,
        }
        
        # Configure logging based on debug mode
        if not logging.getLogger().handlers:
            # Only configure if not already configured
            logging.basicConfig(
                level=logging.DEBUG if debug_mode else logging.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Set logger level for this module
        logger.setLevel(logging.DEBUG if debug_mode else logging.WARNING)
        
        if self.debug_mode:
            logger.debug("[DEBUG] Debug mode enabled")
        
        self.load_commands()

    def _validate_command_module(self, module, module_name: str) -> tuple[bool, Optional[str]]:
        """
        Validates that a command module has the required structure.
        Returns: (is_valid, error_message)
        """
        # Check for execute function
        if not hasattr(module, "execute"):
            return False, f"Missing 'execute' function"
        
        if not callable(module.execute):
            return False, f"'execute' is not callable"
        
        # Validate aliases if present
        if hasattr(module, "aliases"):
            if not isinstance(module.aliases, (list, tuple)):
                return False, f"'aliases' must be a list or tuple, got {type(module.aliases).__name__}"
            
            for alias in module.aliases:
                if not isinstance(alias, str):
                    return False, f"Alias '{alias}' is not a string"
                if not alias:
                    return False, f"Empty alias found"
        
        # Validate description if present
        if hasattr(module, "description"):
            if not isinstance(module.description, str):
                logger.warning(f"[!] Command '{module_name}': description should be a string")
        
        return True, None

    def _check_alias_conflict(self, alias: str, module_name: str) -> bool:
        """
        Checks if an alias conflicts with existing commands or aliases.
        Returns: True if conflict exists, False otherwise
        """
        # Check if alias conflicts with a command name
        if alias in self.commands:
            logger.error(f"[!] Alias conflict: '{alias}' from '{module_name}' conflicts with command '{alias}'")
            return True
        
        # Check if alias is already mapped
        if alias in self.mapping:
            existing = self.mapping[alias]
            logger.error(f"[!] Alias conflict: '{alias}' from '{module_name}' already mapped to '{existing}'")
            return True
        
        return False

    def load_commands(self) -> int:
        """
        Dynamically loads all .py files from the commands/ directory.
        Commands can optionally define an 'aliases' list for shortcuts.
        
        Returns: Number of successfully loaded commands
        """
        self.commands.clear()
        self.mapping.clear()
        self.failed_commands.clear()
        
        loaded_count = 0
        
        # Path to the commands directory
        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        
        if not os.path.exists(commands_dir):
            logger.warning(f"[!] Commands directory not found, creating: {commands_dir}")
            try:
                os.makedirs(commands_dir)
            except OSError as e:
                logger.error(f"[!] Failed to create commands directory: {e}")
            return 0

        # Get list of command files
        try:
            command_files = [f for f in os.listdir(commands_dir) 
                           if f.endswith(".py") and not f.startswith("__")]
        except OSError as e:
            logger.error(f"[!] Failed to list commands directory: {e}")
            return 0
        
        if not command_files:
            logger.warning("[!] No command files found in commands directory")
            return 0

        logger.info(f"[*] Loading commands from {commands_dir}...")
        
        for filename in sorted(command_files):
            module_name = filename[:-3]
            full_module_path = f"commands.{module_name}"
            
            try:
                # Import or reload the module
                if full_module_path in sys.modules:
                    logger.debug(f"[*] Reloading module: {module_name}")
                    module = importlib.reload(sys.modules[full_module_path])
                else:
                    logger.debug(f"[*] Importing module: {module_name}")
                    module = importlib.import_module(full_module_path)
                
                # Validate the command module
                is_valid, error_msg = self._validate_command_module(module, module_name)
                
                if not is_valid:
                    logger.error(f"[!] Invalid command '{module_name}': {error_msg}")
                    self.failed_commands.append(f"{module_name}: {error_msg}")
                    continue
                
                # Register the command
                self.commands[module_name] = module
                loaded_count += 1
                
                # Get description for logging
                description = getattr(module, "description", "No description")
                logger.info(f"[✓] Loaded: {module_name:15s} - {description}")
                
                # Load and validate aliases
                if hasattr(module, "aliases"):
                    alias_count = 0
                    for alias in module.aliases:
                        if not self._check_alias_conflict(alias, module_name):
                            self.mapping[alias] = module_name
                            alias_count += 1
                            logger.debug(f"    └─ Alias: {alias} -> {module_name}")
                    
                    if alias_count > 0:
                        logger.info(f"    └─ Registered {alias_count} alias(es): {', '.join(module.aliases)}")
                        
            except ImportError as e:
                error_detail = f"Import error: {str(e)}"
                logger.error(f"[!] Failed to import '{module_name}': {error_detail}")
                self.failed_commands.append(f"{module_name}: {error_detail}")
                if self.debug_mode:
                    logger.debug(traceback.format_exc())
                    
            except Exception as e:
                error_detail = f"{type(e).__name__}: {str(e)}"
                logger.error(f"[!] Failed to load '{module_name}': {error_detail}")
                self.failed_commands.append(f"{module_name}: {error_detail}")
                if self.debug_mode:
                    logger.debug(traceback.format_exc())
        
        # Summary
        logger.info(f"[*] Command loading complete: {loaded_count} succeeded, {len(self.failed_commands)} failed")
        
        if self.failed_commands and self.debug_mode:
            logger.debug("[*] Failed commands:")
            for failed in self.failed_commands:
                logger.debug(f"    - {failed}")
        
        return loaded_count

    async def _execute_with_timeout(self, command_module, args: List[str], timeout: int) -> str:
        """
        Execute command with timeout handling.
        
        Args:
            command_module: The command module to execute
            args: Command arguments
            timeout: Timeout in seconds
            
        Returns:
            Command output as string
            
        Raises:
            CommandTimeoutError: If execution exceeds timeout
            Exception: Any exception from command execution
        """
        # Check if command is async
        if asyncio.iscoroutinefunction(command_module.execute):
            # Async command
            result = await asyncio.wait_for(
                command_module.execute(args),
                timeout=timeout
            )
        else:
            # Sync command - run in executor to make it awaitable
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, command_module.execute, args),
                timeout=timeout
            )
        
        return result

    def execute(self, command_name: str, args: List[str]) -> str:
        """
        Finds and executes the command with timeout and improved error handling.
        
        Args:
            command_name: The command or alias to execute
            args: List of arguments passed to the command
            
        Returns:
            Command output as string
        """
        # Input validation
        if not isinstance(args, list):
            logger.warning(f"[!] Invalid args type: {type(args).__name__}, converting to list")
            args = [str(args)] if args else []
        
        # Check for aliases (e.g. 'p' -> 'ping')
        target = self.mapping.get(command_name, command_name)
        
        if target not in self.commands:
            logger.warning(f"[!] Unknown command: '{command_name}'")
            
            # Suggest similar commands
            similar = [cmd for cmd in self.commands.keys() if command_name.lower() in cmd.lower()]
            if similar:
                suggestions = ", ".join(similar[:3])
                return f"❌ Unknown command: '{command_name}'\nDid you mean: {suggestions}?"
            
            return f"❌ Unknown command: '{command_name}'\nUse 'help' to see available commands."
        
        # Get timeout for this command
        timeout = Config.get_command_timeout(target)
        
        # Execute the command with timeout
        start_time = time.time()
        
        try:
            logger.debug(f"[*] Executing: {target} with args: {args} (timeout: {timeout}s)")
            
            # Run async execution
            result = asyncio.run(self._execute_with_timeout(
                self.commands[target],
                args,
                timeout
            ))
            
            # Track execution time
            elapsed = time.time() - start_time
            self.execution_stats["success"] += 1
            self.execution_stats["total_execution_time"] += elapsed
            
            logger.debug(f"[✓] Command '{target}' completed in {elapsed:.2f}s")
            
            # Validate result
            if result is None:
                logger.warning(f"[!] Command '{target}' returned None")
                return f"⚠️ Command '{target}' completed but returned no output."
            
            return str(result)
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            self.execution_stats["timeout"] += 1
            self.execution_stats["total_execution_time"] += elapsed
            
            error_msg = f"Command '{target}' exceeded timeout of {timeout}s"
            logger.warning(
                f"[!] Command timeout: {target}",
                extra={
                    'command': target,
                    'timeout': timeout,
                    'elapsed': elapsed,
                }
            )
            
            # User-friendly error message
            return (
                f"⏱️ **Command Timeout**\n\n"
                f"Der Command '{target}' wurde nach {timeout} Sekunden automatisch abgebrochen.\n\n"
                f"**Mögliche Ursachen:**\n"
                f"• Netzwerkprobleme\n"
                f"• Zu große Datenmenge\n"
                f"• System überlastet\n\n"
                f"Bitte versuche es später erneut oder kontaktiere einen Admin."
            )
            
        except TypeError as e:
            elapsed = time.time() - start_time
            self.execution_stats["failed"] += 1
            self.execution_stats["total_execution_time"] += elapsed
            
            error_msg = f"Argument error: {str(e)}"
            logger.error(f"[!] {target}: {error_msg}")
            
            if self.debug_mode:
                logger.debug(traceback.format_exc())
                return f"⚠️ Error in command '{target}':\n{error_msg}\n\nExpected usage: Check command documentation"
            
            return f"⚠️ Error in command '{target}': {error_msg}"
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.execution_stats["failed"] += 1
            self.execution_stats["total_execution_time"] += elapsed
            
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"[!] {target} failed: {error_type}: {error_msg}")
            
            if self.debug_mode:
                logger.debug(traceback.format_exc())
                stack_trace = traceback.format_exc()
                return f"⚠️ {error_type} in command '{target}':\n{error_msg}\n\n```\n{stack_trace}\n```"
            
            return f"⚠️ Error in command '{target}': {error_msg}"
    
    def get_stats(self) -> dict:
        """Returns execution statistics including timeout info"""
        total_executions = (
            self.execution_stats["success"] +
            self.execution_stats["failed"] +
            self.execution_stats["timeout"]
        )
        
        avg_execution_time = 0.0
        if total_executions > 0:
            avg_execution_time = (
                self.execution_stats["total_execution_time"] / total_executions
            )
        
        return {
            "commands_loaded": len(self.commands),
            "aliases_registered": len(self.mapping),
            "failed_loads": len(self.failed_commands),
            "executions_success": self.execution_stats["success"],
            "executions_failed": self.execution_stats["failed"],
            "executions_timeout": self.execution_stats["timeout"],
            "total_execution_time": round(self.execution_stats["total_execution_time"], 2),
            "average_execution_time": round(avg_execution_time, 2),
        }
    
    def list_commands(self) -> List[str]:
        """Returns list of available commands"""
        return sorted(self.commands.keys())
    
    def get_command_info(self, command_name: str) -> Optional[dict]:
        """Returns detailed info about a specific command including timeout"""
        target = self.mapping.get(command_name, command_name)
        
        if target not in self.commands:
            return None
        
        module = self.commands[target]
        aliases = getattr(module, "aliases", [])
        description = getattr(module, "description", "No description available")
        timeout = Config.get_command_timeout(target)
        
        return {
            "name": target,
            "aliases": aliases,
            "description": description,
            "timeout": timeout,
            "has_execute": hasattr(module, "execute"),
        }
