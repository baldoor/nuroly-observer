"""
Help Command - Lists all available commands and their aliases
"""

# Aliases for the help command
aliases = ["h", "start", "?"]

# Short description shown in help menu
description = "List all available commands with their aliases and descriptions"

def execute(args):
    """
    Shows all available commands with descriptions.
    """
    # Import here to avoid circular dependency
    from router import CommandRouter
    
    router = CommandRouter()
    
    response = "📋 **Available Commands:**\n\n"
    
    for cmd_name in sorted(router.commands.keys()):
        module = router.commands[cmd_name]
        
        # Find all aliases for this command
        cmd_aliases = [alias for alias, target in router.mapping.items() if target == cmd_name]
        
        # Get description (with fallback to docstring)
        desc = getattr(module, 'description', None)
        if not desc and hasattr(module, 'execute') and module.execute.__doc__:
            desc = module.execute.__doc__.strip().split('\n')[0]
        
        # Format command line
        if cmd_aliases:
            aliases_str = ', '.join([f'`{a}`' for a in cmd_aliases])
            line = f"• `{cmd_name}` ({aliases_str})"
        else:
            line = f"• `{cmd_name}`"
        
        # Add description if available
        if desc:
            line += f" - {desc}"
        
        response += line + "\n"
    
    response += "\n💡 Tip: Use shortcuts for faster access!"
    
    return response
