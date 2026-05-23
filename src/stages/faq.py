"""Stage 1: FAQ Answering — utility functions.

The core FAQ answering logic is handled by the Gemini model through
the system prompt (which contains the full SOP). This module provides
helper functions for the FAQ stage.
"""


# Exit commands that signal the user wants to end the session
EXIT_COMMANDS = {"quit", "exit", "bye", "goodbye", "end", "done", "close"}


def is_exit_command(user_input: str) -> bool:
    """Check if the user's input is an exit command.

    Args:
        user_input: Raw user input string.

    Returns:
        True if the user wants to end the conversation.
    """
    return user_input.strip().lower() in EXIT_COMMANDS
