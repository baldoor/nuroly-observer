from typing import Dict, NamedTuple
from .token_bucket import TokenBucket


class LimitCheck(NamedTuple):
    """Result of a rate limit check.
    
    Attributes:
        allowed: Whether the action is allowed
        wait_time: Time in seconds to wait if not allowed (0 if allowed)
    """
    allowed: bool
    wait_time: float = 0.0


class RateLimiter:
    """Rate limiter that manages token buckets per user.
    
    Each user gets their own token bucket for independent rate limiting.
    Prevents command flooding and resource exhaustion.
    
    Args:
        max_tokens: Maximum burst capacity per user
        tokens_per_minute: Refill rate (tokens added per minute)
    
    Example:
        >>> limiter = RateLimiter(max_tokens=10, tokens_per_minute=10)
        >>> check = limiter.check_limit("user123")
        >>> if check.allowed:
        ...     execute_command()
        ... else:
        ...     print(f"Wait {check.wait_time} seconds")
    """
    
    def __init__(self, max_tokens: int = 10, tokens_per_minute: int = 10):
        self.max_tokens = max_tokens
        self.refill_rate = tokens_per_minute / 60  # Convert to tokens per second
        self.buckets: Dict[str, TokenBucket] = {}
    
    def _get_bucket(self, user_id: str) -> TokenBucket:
        """Gets or creates a token bucket for a user."""
        if user_id not in self.buckets:
            self.buckets[user_id] = TokenBucket(
                self.max_tokens, 
                self.refill_rate
            )
        return self.buckets[user_id]
    
    def check_limit(self, user_id: str) -> LimitCheck:
        """Checks if a user can execute a command.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            LimitCheck with allowed status and optional wait time
        """
        bucket = self._get_bucket(user_id)
        
        if bucket.try_consume(1):
            return LimitCheck(allowed=True)
        
        return LimitCheck(
            allowed=False, 
            wait_time=bucket.get_wait_time()
        )
    
    def get_status(self, user_id: str) -> Dict[str, float]:
        """Returns current rate limit status for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with 'available' tokens and 'wait_time'
        """
        bucket = self._get_bucket(user_id)
        return {
            'available': bucket.get_available_tokens(),
            'wait_time': bucket.get_wait_time()
        }
    
    def reset_user(self, user_id: str) -> None:
        """Resets rate limit for a specific user (admin function)."""
        if user_id in self.buckets:
            del self.buckets[user_id]
