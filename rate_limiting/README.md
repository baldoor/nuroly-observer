# Rate Limiting

This module implements rate limiting using the Token Bucket algorithm to prevent command flooding and resource exhaustion.

## How It Works

### Token Bucket Algorithm

Imagine each user has a bucket that can hold a maximum number of tokens (coins):

1. **Starting state**: Bucket is full (e.g., 10 tokens)
2. **Command execution**: User needs 1 token to execute a command
3. **Refill**: Tokens automatically refill over time (e.g., 1 token every 6 seconds = 10 per minute)
4. **Limit**: Bucket never overflows (maximum stays at 10)

### Example Scenario

```
User starts with 10 tokens:
- Executes 3 commands quickly → 7 tokens left
- Waits 30 seconds → 5 new tokens added → 10 tokens (capped at max)
- Executes 15 commands rapidly → After 10th: Rate limit exceeded!
- Must wait 6 seconds → 1 new token → Can continue
```

## Usage

### Basic Integration

```python
from rate_limiting import RateLimiter
import math

# Initialize rate limiter
limiter = RateLimiter(max_tokens=10, tokens_per_minute=10)

# Check before executing command
def handle_command(user_id: str, command: str):
    check = limiter.check_limit(user_id)
    
    if not check.allowed:
        wait_seconds = math.ceil(check.wait_time)
        return f"⏱️ Rate limit exceeded! Wait {wait_seconds}s"
    
    # Execute command
    return execute_command(command)
```

### Get User Status

```python
status = limiter.get_status("user123")
print(f"Available commands: {status['available']}")
print(f"Wait time: {status['wait_time']:.1f}s")
```

## Configuration

Configure via environment variables in `.env`:

```bash
# Maximum burst capacity (tokens in bucket)
RATE_LIMIT_MAX_TOKENS=10

# Refill rate (tokens added per minute)
RATE_LIMIT_TOKENS_PER_MINUTE=10
```

### Recommended Settings

- **Lenient**: `max_tokens=15`, `tokens_per_minute=10` (allows occasional bursts)
- **Balanced**: `max_tokens=10`, `tokens_per_minute=10` (default, good for most cases)
- **Strict**: `max_tokens=5`, `tokens_per_minute=5` (for high-security environments)

## Benefits

✅ **Prevents abuse**: Users can't flood the system with unlimited commands  
✅ **Fair usage**: Each user has independent limits  
✅ **Flexible**: Allows short bursts while preventing sustained spam  
✅ **User-friendly**: Clear error messages with wait times  
✅ **Lightweight**: No database required, runs in-memory  

## Architecture

```
rate_limiting/
├── __init__.py          # Public exports
├── token_bucket.py      # Core Token Bucket algorithm
├── rate_limiter.py      # User-level rate limiting
└── README.md            # This file
```

## Testing

Test the rate limiter:

```python
import time
from rate_limiting import RateLimiter

limiter = RateLimiter(max_tokens=3, tokens_per_minute=60)  # 1 per second

# First 3 commands should work
for i in range(3):
    assert limiter.check_limit("test_user").allowed

# 4th command should fail
assert not limiter.check_limit("test_user").allowed

# After 1 second, should work again
time.sleep(1)
assert limiter.check_limit("test_user").allowed
```
