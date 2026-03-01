# Examples

This folder contains examples and templates for the nuroly-observer framework.

## Available Examples

### Command Templates

- **[basic_command.py](basic_command.py)** - Simple command example for getting started
- **[command_template.py](command_template.py)** - Complete template with all features

### Integration Examples

- **[shodan/](shodan/)** - Complete Shodan API integration
  - Shows how to integrate external APIs
  - Includes error handling and environment variables
  - Complex query processing with multiple sub-commands
  - See [shodan/README.md](shodan/README.md) for details

## How to Use These Examples?

### 1. Copy Command Template

```powershell
# Windows
Copy-Item .\examples\command_template.py .\commands\mycommand.py

# Linux/Mac
cp ./examples/command_template.py ./commands/mycommand.py
```

### 2. Customize Command

Open the copied file and adjust the following:
- `aliases` - Shortcuts for your command
- `description` - Description for the help menu
- `execute()` - Your command logic

### 3. Restart Bot

The new command will be automatically loaded by the router!

## Best Practices

- ✅ Use meaningful error messages
- ✅ Validate inputs before processing them
- ✅ Document your commands with docstrings
- ✅ Use private helper functions (`_helper_name()`)
- ✅ Test edge cases (no args, too many args, etc.)
- ✅ Use emojis for better UX (optional)

## Want More Examples?

Check out the existing commands in the `commands/` folder:
- `ping.py` - Minimal example
- `help.py` - Dynamic command listing
- `status.py` - System information with psutil
- `shodan.py` - API integration (active)
