# Debugging & Troubleshooting Guide

This guide covers debugging features, error handling, and common issues when working with Nuroly-Observer.

---

## Debug Mode

Nuroly-Observer includes a comprehensive debug mode to help diagnose issues with commands or the bot itself.

### Enable Debug Mode

Set `DEBUG=true` in your `.env` file:

```dotenv
DEBUG=true
```

### What Debug Mode Provides

- ✅ **Detailed Command Loading**: See exactly which commands load successfully and which fail
- ✅ **Full Stack Traces**: Get complete error traces when commands fail to import or execute
- ✅ **Alias Tracking**: Monitor alias registration and detect conflicts
- ✅ **Execution Logging**: Track every command execution with arguments
- ✅ **Module Validation**: Detailed checks for required functions, valid aliases, and proper structure

### Example Output (Debug Mode ON)

```
2026-03-01 17:36:44 - DEBUG - [DEBUG] Debug mode enabled
2026-03-01 17:36:44 - INFO - [*] Loading commands from .../commands...
2026-03-01 17:36:44 - DEBUG - [*] Importing module: help
2026-03-01 17:36:44 - INFO - [✓] Loaded: help - List all available commands
2026-03-01 17:36:44 - DEBUG -     └─ Alias: h -> help
2026-03-01 17:36:44 - ERROR - [!] Failed to import 'mycommand': Import error: No module named 'requests'
2026-03-01 17:36:44 - DEBUG - Traceback (most recent call last):
  ...
ModuleNotFoundError: No module named 'requests'
```

---

## Error Handling Features

The command router includes intelligent error handling built-in:

### 1. Graceful Degradation
- Failed commands don't crash the entire bot
- Other commands continue to work normally
- Clear error messages for missing dependencies

### 2. Command Validation
When loading commands, the router validates:
- Presence of required `execute()` function
- That `execute` is callable
- Alias structure and types (must be list/tuple of strings)
- Description field (optional, but validates if present)

### 3. Smart Error Messages
- Suggests similar commands on typos
- Provides context-aware error details
- User-friendly emoji indicators (✅ ❌ ⚠️)

**Example:**
```
❌ Unknown command: 'pign'
Did you mean: ping?
```

### 4. Execution Statistics
Track your bot's health with:
- Successful vs. failed command executions
- Number of loaded commands and registered aliases
- Failed command loads with reasons

Access with `router.get_stats()`:
```python
{
    'commands_loaded': 3,
    'aliases_registered': 6,
    'failed_loads': 0,
    'executions_success': 42,
    'executions_failed': 1,
    'executions_timeout': 0,
    'total_execution_time': 12.34,
    'average_execution_time': 0.29
}
```

---

## Common Issues

### Command not loading?

**Checklist:**
1. Enable debug mode to see the full error: `DEBUG=true`
2. Check if all required modules are installed: `pip install -r requirements.txt`
3. Verify your command has an `execute(args)` function
4. Ensure the file ends with `.py` and doesn't start with `__`
5. Check the console output on bot startup for error messages

**Debug Process:**
```bash
# Enable debug mode
echo "DEBUG=true" >> .env

# Run the bot and watch the logs
python main.py
```

### Missing module error?

```
ModuleNotFoundError: No module named 'psutil'
```

**Solution:**
Install the missing package:
```bash
pip install psutil
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### Alias conflicts?

The router will warn you if an alias conflicts with a command name or another alias:

```
[!] Alias conflict: 'h' from 'mycommand' already mapped to 'help'
```

**Solution:**
Choose a different alias in your command file:
```python
# Change from
aliases = ["h"]

# To something unique
aliases = ["mc", "mycmd"]
```

### Command returns None?

If your command's `execute()` function doesn't return anything:

```
⚠️ Command 'mycommand' completed but returned no output.
```

**Solution:**
Always return a string from your execute function:
```python
def execute(args):
    # Do something
    return "Done!"  # Always return something
```

### TypeError on command execution?

```
⚠️ Error in command 'mycommand': Argument error: ...
```

**Common causes:**
- Your `execute()` function expects specific arguments
- Arguments are not properly parsed

**Solution:**
Handle variable arguments gracefully:
```python
def execute(args):
    # Validate arguments
    if not args:
        return "❌ Usage: !mycommand <argument>"
    
    # Your logic here
    return f"Processed: {args[0]}"
```

---

## Advanced Debugging

### Inspecting Router State

You can inspect the router's internal state for debugging:

```python
from router import CommandRouter

router = CommandRouter(debug_mode=True)

# List all loaded commands
print(router.list_commands())

# Get info about a specific command
info = router.get_command_info('ping')
print(info)
# {'name': 'ping', 'aliases': ['p'], 'description': 'ICMP ping', 'timeout': 5}

# Check statistics
print(router.get_stats())
```

### Testing Commands Directly

Test commands without running the full bot:

```python
import asyncio
from router import CommandRouter


async def main():
    router = CommandRouter(debug_mode=True)
    # Execute a command directly (async)
    result = await router.execute('ping', ['8.8.8.8'])
    print(result)


asyncio.run(main())
```

### Logging Configuration

The router uses Python's `logging` module. You can customize logging behavior:

```python
import logging

# Set custom log level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Best Practices

1. **Always test with DEBUG mode first** when developing new commands
2. **Add proper error handling** in your commands' `execute()` functions
3. **Return meaningful messages** - avoid returning None or empty strings
4. **Validate user input** - check args length and types before processing
5. **Add descriptions** to all commands for better discoverability
6. **Use unique aliases** to avoid conflicts
7. **Keep dependencies minimal** - only import what you need

---

## Getting Help

If you're still experiencing issues:

1. Check the [README](../README.md) for general setup
2. Review the [command templates](../examples/) for working examples
3. Enable debug mode and examine the full error output
4. Check that all environment variables are properly set in `.env`

For platform-specific setup issues, see:
- [Telegram Setup Guide](telegram_setup.md)
- [Slack Setup Guide](slack_setup.md)
