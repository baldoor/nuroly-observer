import time
from typing import Optional


class TokenBucket:
    """Token Bucket algorithm for rate limiting.
    
    Each bucket holds a maximum number of tokens that refill over time.
    When a user wants to execute a command, they must consume a token.
    
    Args:
        max_tokens: Maximum capacity of the bucket (burst size)
        refill_rate: Tokens added per second (e.g., 10/60 = 10 per minute)
    """
    
    def __init__(self, max_tokens: int = 10, refill_rate: float = 10/60):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = float(max_tokens)  # Start with full bucket
        self.last_refill_time = time.time()
    
    def _refill(self) -> None:
        """Adds new tokens based on elapsed time since last refill."""
        now = time.time()
        time_passed = now - self.last_refill_time
        tokens_to_add = time_passed * self.refill_rate
        
        # Add tokens but don't exceed maximum
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill_time = now
    
    def try_consume(self, tokens: int = 1) -> bool:
        """Attempts to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume (default: 1)
            
        Returns:
            True if tokens were available and consumed, False otherwise
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def get_available_tokens(self) -> int:
        """Returns the number of available tokens (rounded down)."""
        self._refill()
        return int(self.tokens)
    
    def get_wait_time(self) -> float:
        """Returns wait time in seconds until next token is available."""
        self._refill()
        if self.tokens >= 1:
            return 0.0
        
        tokens_needed = 1 - self.tokens
        return tokens_needed / self.refill_rate
