"""
Template for custom commands

Copy this file to commands/ or custom_commands/ 
and rename it according to your command.
"""

# Optional: Define shortcuts (aliases) for this command
# Example: aliases = ["m", "msg"]
aliases = []

# Optional: Short description shown in help menu
description = "Brief description of what this command does"

def execute(args):
    """
    Main function executed when the command is called.
    
    Args:
        args (list): List of passed arguments
                     Example: "!mycommand foo bar" -> args = ["foo", "bar"]
    
    Returns:
        str: The response message sent back to the user
    """
    
    # Example: Check if arguments were passed
    if not args:
        return "❌ Please provide at least one argument!"
    
    # Example: Process the arguments
    user_input = " ".join(args)
    
    # Example: Return response
    return f"✅ You entered: {user_input}"


# Optional: Additional helper functions
def _helper_function():
    """Private helper functions with _ prefix"""
    pass
