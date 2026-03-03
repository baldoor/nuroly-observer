# Command Timeouts

## Overview

The command timeout feature prevents commands from running indefinitely by automatically terminating them after a configured time limit. This helps:

- Prevent hanging commands from blocking the bot
- Free up resources when commands take too long
- Provide clear feedback to users when timeouts occur

## Configuration

### Default Timeout

Set the default timeout for all commands in your `.env` file:

```bash
DEFAULT_COMMAND_TIMEOUT=30  # seconds
```

### Command-Specific Timeouts

You can configure specific timeouts for individual commands:

**Option 1: Environment Variables**

```bash
TIMEOUT_STATUS=5
TIMEOUT_PING=10
TIMEOUT_BACKUP=300
TIMEOUT_REBOOT=120
```

**Option 2: Per-command default (recommended)**

In each command module you can define a natural default timeout:

```python
# commands/backup.py
timeout = 300  # seconds
```

**Option 3: Global default (command_timeout.py)**

```python
from command_timeout import DEFAULT_COMMAND_TIMEOUT

print(DEFAULT_COMMAND_TIMEOUT)  # configured via ENV DEFAULT_COMMAND_TIMEOUT
```

### Priority Order

1. Environment variable (`TIMEOUT_<COMMAND_NAME>`)
2. `timeout` attribute in the command module (if present)
3. `DEFAULT_COMMAND_TIMEOUT` in `command_timeout.py`

## Usage

### For Command Developers

No changes needed! All commands automatically get timeout protection.

**Sync Commands:**
```python
def execute(args):
    # Your command logic
    return "Result"
```

**Async Commands:**
```python
async def execute(args):
    # Your async command logic
    await asyncio.sleep(1)
    return "Result"
```

### For Users

When a command times out, you'll see:

```
⏱️ Command Timeout

The command 'backup' was automatically aborted after 300 seconds.

Possible causes:
• Network issues
• Data set too large
• System under heavy load

Please try again later or contact an administrator.
```

## Monitoring

### Execution Statistics

Get timeout statistics via `router.get_stats()`:

```python
{
    "commands_loaded": 10,
    "aliases_registered": 5,
    "executions_success": 42,
    "executions_failed": 2,
    "executions_timeout": 3,  # Number of timeouts
    "total_execution_time": 156.45,
    "average_execution_time": 3.32
}
```

### Logging

Timeouts are logged with full context:

```
2026-03-02 20:00:00 - WARNING - [!] Command timeout: backup
```

With extra fields:
- `command`: Command name
- `timeout`: Configured timeout
- `elapsed`: Actual elapsed time

## Best Practices

### Choosing Timeout Values

- **Quick queries** (status, help): 5-10 seconds
- **Network operations** (ping, API calls): 10-30 seconds
- **File operations** (backup, download): 60-300 seconds
- **System operations** (reboot, updates): 120-600 seconds

### Handling Timeouts in Commands

**Good:**
```python
def execute(args):
    try:
        # Your logic
        return result
    finally:
        # Cleanup code runs even on timeout
        cleanup_resources()
```

**Better:**
```python
import signal

def execute(args):
    # Register cleanup handler
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    # Your logic
    return result
```

### Testing

Test your commands with realistic timeouts:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_command_timeout():
    async def slow_command():
        await asyncio.sleep(10)
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_command(), timeout=1)
```

## Troubleshooting

### Command Always Timing Out

1. **Check timeout configuration**: Is it set too low?
2. **Review command logic**: Can it be optimized?
3. **Increase timeout**: Adjust in config for that specific command

### Timeout Not Working

1. **Check config loading**: Verify `.env` is loaded
2. **Verify command name**: Must match exactly (case-sensitive)
3. **Check logs**: Look for configuration errors

### False Positives

If commands legitimately need longer:

```bash
# Increase specific command timeout
TIMEOUT_LONG_RUNNING_TASK=600
```

## Architecture

### Components

1. **exceptions.py**: `CommandTimeoutError` exception
2. **command_timeout.py**: Timeout configuration helpers (global + per-command)
3. **router.py**: Timeout enforcement in command execution
4. **tests/test_timeout.py**: Timeout-related test suite

### Flow

```
User Command
    ↓
CommandRouter.execute()
    ↓
get_command_timeout() from command_timeout.py
    ↓
_execute_with_timeout()
    ↓
asyncio.wait_for(command, timeout)
    ↓
Success / TimeoutError / Exception
    ↓
Log & Return Result
```

## Performance Impact

Minimal overhead:
- Async wrapper: ~0.1ms
- Time tracking: ~0.05ms
- Timeout lookup: ~0.01ms

Total: **~0.2ms per command execution**

## Future Enhancements

- [ ] Per-user timeout limits
- [ ] Adaptive timeouts based on historical execution times
- [ ] Graceful degradation (warning before timeout)
- [ ] Prometheus metrics export
- [ ] Timeout events via webhooks
