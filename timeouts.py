"""Command timeout configuration helpers.

Provides a simple, explicit model:

- Global default timeout via environment variable DEFAULT_COMMAND_TIMEOUT
- Optional per-command timeout via TIMEOUT_<COMMAND_NAME> env vars
- Optional per-command default via a ``timeout`` attribute on the command module
"""

import os
from typing import Optional

# Global default timeout (seconds), can be overridden via env DEFAULT_COMMAND_TIMEOUT
DEFAULT_COMMAND_TIMEOUT: int = int(os.getenv("DEFAULT_COMMAND_TIMEOUT", "30"))


def get_command_timeout(command_name: str, module: Optional[object] = None) -> int:
    """Resolve the effective timeout for a command.

    Priority:
    1. Environment variable: TIMEOUT_<COMMAND_NAME>
    2. ``timeout`` attribute on the command module (if provided and int)
    3. Global DEFAULT_COMMAND_TIMEOUT
    """
    # 1) Environment override
    env_var = f"TIMEOUT_{command_name.upper()}"
    env_timeout = os.getenv(env_var)
    if env_timeout is not None:
        try:
            return int(env_timeout)
        except ValueError:
            # Invalid env value -> ignore and fall through to next source
            pass

    # 2) Command-local default (module.timeout)
    if module is not None:
        module_timeout = getattr(module, "timeout", None)
        if isinstance(module_timeout, int):
            return module_timeout

    # 3) Global default
    return DEFAULT_COMMAND_TIMEOUT
