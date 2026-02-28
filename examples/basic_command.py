def execute(args):
    """
    Template for creating new Nuroly-Observer commands.
    Drop this file into the /commands folder to activate it.
    """
    if not args:
        return "Hello! You didn't provide any arguments."
    
    return f"Admin Command executed with: {' '.join(args)}"