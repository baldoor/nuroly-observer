# Nuroly-Observer

**Nuroly-Observer** is a lightweight, asynchronous, and modular ChatOps bot framework. 
It is designed to run concurrently on multiple platforms (like Telegram and Slack) while maintaining a highly secure, user-restricted environment. It perfectly serves as a "HomeOps" or DevOps assistant to run infrastructure scripts directly from your favorite chat app.

## Key Features

- **Multi-Platform Support:** Runs on Telegram and Slack simultaneously using non-blocking `asyncio`.
- **Security:** Strict User-ID based whitelists ensure that only authorized users can execute commands.
- **Plug-and-Play Commands:** Add new functionality by simply dropping a `.py` file into the commands directory. No need to touch the core routing logic.
- **Private by Default:** All command files are automatically gitignored, keeping your infrastructure scripts safe from accidental commits.
- **Command Aliases:** Each command can define its own shortcuts (e.g., type `!p` to execute the `ping` command).
- **Dynamic Bot Menus:** Telegram command menu is automatically generated from your commands and descriptions on startup.

---

## Project Structure

```text
nuroly-observer/
├── main.py                 # Core engine (async orchestration & security checks)
├── router.py               # Dynamic module loader and command aliasing
├── providers/              # Platform-specific adapters (Slack, Telegram, etc.)
├── commands/               # Your bot commands (gitignored - only structure tracked)
├── examples/               # Command templates and examples
├── docs/                   # Setup guides and documentation
├── .env.example            # Template for your secrets and API keys
└── requirements.txt        # Python dependencies
```

---

## Getting Started

### 1. Prerequisites & Platform Setup
- Python 3.8+
- Set up your chat platforms using our step-by-step guides:
  - [How to set up the Telegram Bot](docs/telegram_setup.md)
  - [How to set up the Slack App (Socket Mode)](docs/slack_setup.md)

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone [https://github.com/baldoor/nuroly-observer.git](https://github.com/baldoor/nuroly-observer.git)
cd nuroly-observer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the environment template and insert your keys:

```bash
cp .env.example .env
```

Open the `.env` file and configure your tokens and security whitelists:
- **`TELEGRAM_ALLOWED_USERS`**: Your numeric Telegram User-ID (e.g., `123456789`).
- **`SLACK_ALLOWED_USERS`**: Your alphanumeric Slack Member-ID (e.g., `U0123ABCD`).
- **Prefixes**: Choose your preferred command triggers (e.g., `/` for Telegram, `!` for Slack).
- **`DEBUG`**: Set to `true` to enable detailed error logs with stack traces (default: `false`).

### 4. Run the Bot

```bash
python main.py
```

You should see terminal outputs confirming that the security whitelists are loaded and the bots have successfully started polling.

---

## Debugging & Troubleshooting

### Debug Mode

Nuroly-Observer includes a comprehensive debug mode to help diagnose issues with commands or the bot itself.

**Enable Debug Mode:**

Set `DEBUG=true` in your `.env` file:

```dotenv
DEBUG=true
```

**What Debug Mode Provides:**

- ✅ **Detailed Command Loading**: See exactly which commands load successfully and which fail
- ✅ **Full Stack Traces**: Get complete error traces when commands fail to import or execute
- ✅ **Alias Tracking**: Monitor alias registration and detect conflicts
- ✅ **Execution Logging**: Track every command execution with arguments
- ✅ **Module Validation**: Detailed checks for required functions, valid aliases, and proper structure

**Example Output (Debug Mode ON):**

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

### Error Handling Features

The command router includes intelligent error handling:

**1. Graceful Degradation**
- Failed commands don't crash the entire bot
- Other commands continue to work normally
- Clear error messages for missing dependencies

**2. Command Validation**
- Checks for required `execute()` function
- Validates alias structure and types
- Detects alias conflicts between commands

**3. Smart Error Messages**
- Suggests similar commands on typos
- Provides context-aware error details
- User-friendly emoji indicators (✅ ❌ ⚠️)

**4. Execution Statistics**
- Tracks successful vs. failed command executions
- Monitors loaded commands and registered aliases
- Provides runtime diagnostics

### Common Issues

**Command not loading?**
1. Enable debug mode to see the full error
2. Check if all required modules are installed: `pip install -r requirements.txt`
3. Verify your command has an `execute(args)` function
4. Ensure the file ends with `.py` and doesn't start with `__`

**Missing module error?**
```
ModuleNotFoundError: No module named 'psutil'
```
Install the missing package:
```bash
pip install psutil
```

**Alias conflicts?**
The router will warn you if an alias conflicts with a command name or another alias:
```
[!] Alias conflict: 'h' from 'mycommand' already mapped to 'help'
```
Choose a different alias in your command file.

---

## Writing Commands

Creating a new command is incredibly simple. Create a `.py` file matching your command name in the `commands/` folder.

**Example: `commands/hello.py`**

```python
# Optional: Define shortcuts for your command
aliases = ["hi", "hey"]

# Optional: Short description for help menu
description = "Greet users with a friendly message"

def execute(args):
    """
    args: A list of arguments passed after the command.
    Example: '!hello world' -> args = ['world']
    """
    if args:
        return f"Hello, {' '.join(args)}!"
    return "Hello there!"
```

Once saved, the command is instantly available via `!hello`, `!hi`, or `!hey` (on Slack) or `/hello`, `/hi`, `/hey` (on Telegram) upon the next bot restart.

### Command Aliases

Each command can define its own aliases (shortcuts). Simply add an `aliases` list at the top of your command file:

```python
aliases = ["p", "pg"]  # Now your command works with shortcuts!
```

### Command Descriptions

Add a `description` field to make your commands discoverable in the help menu:

```python
description = "Brief description of what this command does"
```

The help command will automatically display this description. If no description is provided, it falls back to the execute function's docstring.

The router automatically loads aliases and descriptions when starting. No need to modify the core code!

### Telegram Bot Menu

The Telegram provider automatically generates a bot command menu from your available commands. When users type `/` in a Telegram chat with your bot, they'll see an interactive menu showing:
- All available commands
- Their descriptions
- Direct shortcuts to execute them

This menu is dynamically updated on each bot startup, so adding new commands or changing descriptions is automatically reflected without any additional configuration.

**Note:** This feature is Telegram-specific. Slack uses a different command registration system.

## Security & Best Practices

1. **Commands are Private by Default:** All `.py` files in `commands/` are automatically gitignored (except `help.py`, which serves as a working example and is included in the repository). Only the directory structure (`.gitkeep`, `README.md`) is tracked. This prevents accidental leaks of IPs, paths, or sensitive credentials in your infrastructure scripts.

2. **Whitelist Only Trusted Users:** Ensure your `.env` contains **only your User ID** in the whitelist. The bot drops any message from unlisted users before it even reaches the command router.

3. **Use the Template:** Check `examples/command_template.py` for a ready-to-use command skeleton with best practices.

4. **Add Descriptions:** Always add a `description` field to your commands. This makes them discoverable in the help menu and Telegram's bot command menu.