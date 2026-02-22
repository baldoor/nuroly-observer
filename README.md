# Nuroly-Observer

**Nuroly-Observer** is a lightweight, asynchronous, and modular ChatOps bot framework. 
It is designed to run concurrently on multiple platforms (like Telegram and Slack) while maintaining a highly secure, user-restricted environment. It perfectly serves as a "HomeOps" or DevOps assistant to run infrastructure scripts directly from your favorite chat app.

## Key Features

- **Multi-Platform Support:** Runs on Telegram and Slack simultaneously using non-blocking `asyncio`.
- **Bulletproof Security:** Strict User-ID based whitelists ensure that only authorized users can execute commands.
- **Plug-and-Play Commands:** Add new functionality by simply dropping a `.py` file into the commands directory. No need to touch the core routing logic.
- **Private ChatOps (`custom_commands/`):** Features a built-in two-folder architecture. Keep your generic commands in `commands/` for the public, and put your private infrastructure scripts into `custom_commands/` (which is safely ignored by Git).
- **Command Aliases:** Built-in alias mapping (e.g., type `!p` to execute the `ping` command).

---

## Project Structure

```text
nuroly-observer/
├── main.py                 # Core engine (async orchestration & security checks)
├── router.py               # Dynamic module loader and command aliasing
├── providers/              # Platform-specific adapters (Slack, Telegram, etc.)
├── commands/               # Public commands (e.g., ping.py, help.py)
├── custom_commands/        # PRIVATE commands (ignored by git - for your server scripts)
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

### 4. Run the Bot

```bash
python main.py
```

You should see terminal outputs confirming that the security whitelists are loaded and the bots have successfully started polling.

---

## Writing Commands

Creating a new command is incredibly simple. Create a `.py` file matching your command name in either the `commands/` or `custom_commands/` folder.

**Example: `commands/hello.py`**

```python
def execute(args):
    """
    args: A list of arguments passed after the command.
    Example: '!hello world' -> args = ['world']
    """
    if args:
        return f"Hello, {' '.join(args)}!"
    return "Hello there!"
```

Once saved, the command is instantly available via `!hello` (on Slack) or `/hello` (on Telegram) upon the next bot restart.

## Security & Best Practices

If you use this bot to execute system commands (like a ping check, restarting Docker containers, etc.):
1. **Always** place those scripts inside the `custom_commands/` directory. Git is configured to ignore this folder, preventing accidental leaks of IPs, paths, or passwords.
2. Ensure your `.env` contains **only your User ID** in the whitelist. The bot drops any message from unlisted users before it even reaches the command router.