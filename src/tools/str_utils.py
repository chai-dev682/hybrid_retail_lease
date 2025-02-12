from typing import List

from src.agents.graph_state import Message


def messages_to_text(messages: List[Message]) -> str:
    """Transforms a list of Message objects into a single text string.

    Args:
      messages: A list of Message objects.

    Returns:
      A string representation of the messages.
    """
    text = ""
    for message in messages:
        text += f"{message.role.value}: {message.content}\n"
    return text
