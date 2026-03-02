"""Configuration management for nuroly-observer"""

import os
from typing import Dict, Optional


class Config:
    """Central configuration class"""
    
    # Default timeout for all commands (seconds)
    DEFAULT_COMMAND_TIMEOUT: int = int(os.getenv('DEFAULT_COMMAND_TIMEOUT', '30'))
    
    # Command-specific timeouts (can be overridden via environment)
    COMMAND_TIMEOUTS: Dict[str, int] = {
        'status': 5,
        'ping': 10,
        'help': 5,
        'echo': 5,
        # Add more command-specific timeouts here
    }
    
    @classmethod
    def get_command_timeout(cls, command_name: str) -> int:
        """
        Get timeout for a specific command.
        
        Priority:
        1. Environment variable: TIMEOUT_<COMMAND_NAME>
        2. COMMAND_TIMEOUTS dict
        3. DEFAULT_COMMAND_TIMEOUT
        
        Args:
            command_name: Name of the command
            
        Returns:
            Timeout in seconds
        """
        # Check environment variable first
        env_var = f'TIMEOUT_{command_name.upper()}'
        env_timeout = os.getenv(env_var)
        
        if env_timeout:
            try:
                return int(env_timeout)
            except ValueError:
                pass
        
        # Check command-specific config
        if command_name in cls.COMMAND_TIMEOUTS:
            return cls.COMMAND_TIMEOUTS[command_name]
        
        # Return default
        return cls.DEFAULT_COMMAND_TIMEOUT
    
    @classmethod
    def set_command_timeout(cls, command_name: str, timeout: int) -> None:
        """Set timeout for a specific command at runtime"""
        cls.COMMAND_TIMEOUTS[command_name] = timeout
