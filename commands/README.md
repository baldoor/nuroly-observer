# Commands Directory

This directory contains your bot commands. All `.py` files here are automatically loaded by the router.

## Creating a Command

Create a `.py` file with the following structure:

```python
# Optional: Define shortcuts for this command
aliases = ["shortcut"]

# Optional: Short description for help menu
description = "Brief description of what this command does"

def execute(args):
    """
    Main function called when the command is executed.
    
    Args:
        args (list): List of arguments passed to the command
                     Example: "!mycommand foo bar" -> args = ["foo", "bar"]
    
    Returns:
        str: Response message sent to the user
    """
    if not args:
        return "❌ Please provide arguments!"
    
    return f"✅ You said: {' '.join(args)}"
```

## Command Aliases

Add an `aliases` list at the top of your file to enable shortcuts:

```python
aliases = ["p", "pg"]  # Command can be called with these shortcuts
```

## Command Descriptions

Add a `description` field to make your command visible in the help menu:

```python
description = "Check if a host is reachable via ICMP ping"
```

The help command (`!help` or `!h`) will display all commands with their aliases and descriptions.

## Examples

Check out the `examples/command_template.py` for a complete template.

## Note

**All command files are gitignored by default** to keep your personal/infrastructure scripts private. Only this README and `.gitkeep` are tracked in version control.
