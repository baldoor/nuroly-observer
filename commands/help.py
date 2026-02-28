"""
Help Command - Lists all available commands and their aliases
"""

# Aliases for the help command
aliases = ["h", "start", "?"]

def execute(args):
    """
    Shows all available commands.
    """
    # Import here to avoid circular dependency
    from router import CommandRouter
    
    router = CommandRouter()
    
    response = "📋 **Available Commands:**\n\n"
    
    for cmd_name in sorted(router.commands.keys()):
        # Find all aliases for this command
        cmd_aliases = [alias for alias, target in router.mapping.items() if target == cmd_name]
        
        if cmd_aliases:
            response += f"• `{cmd_name}` (Aliases: {', '.join([f'`{a}`' for a in cmd_aliases])})\n"
        else:
            response += f"• `{cmd_name}`\n"
    
    response += "\n💡 Tip: Use shortcuts for faster access!"
    
    return response
