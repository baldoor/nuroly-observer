"""Custom exceptions for nuroly-observer"""


class CommandTimeoutError(Exception):
    """Raised when command execution exceeds configured timeout"""
    
    def __init__(self, message: str, command: str, timeout: int, elapsed: float = None):
        self.command = command
        self.timeout = timeout
        self.elapsed = elapsed
        super().__init__(message)
    
    def __str__(self):
        base_msg = f"Command '{self.command}' exceeded timeout of {self.timeout}s"
        if self.elapsed:
            base_msg += f" (elapsed: {self.elapsed:.2f}s)"
        return base_msg
