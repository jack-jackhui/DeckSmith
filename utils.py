"""Utility functions for DeckSmith."""

from typing import Any, Dict, Union


def clean_response(response: Union[str, Dict[str, Any]]) -> str:
    """Clean and format a chatbot response for display.

    Args:
        response: The raw response, either a string or dictionary with 'response' key.

    Returns:
        A cleaned and formatted response string.
    """
    if isinstance(response, dict):
        response = response.get('response', '')

    if not isinstance(response, str):
        response = str(response)

    response = response.replace("{", "").replace("}", "").replace("\"", "")

    response = response.replace("\n\n", "\n")
    response = response.replace("  ", " ")

    replacements = {
        "\u2022": "-",
        "\u27a2": "-",
        "\u2023": "-",
        "\u25aa": "-",
        "\u25ab": "-",
    }
    for old, new in replacements.items():
        response = response.replace(old, new)

    lines = response.split("\n")
    formatted_lines = []
    for line in lines:
        if line.startswith("-"):
            formatted_lines.append(f"- {line[1:].strip()}")
        else:
            formatted_lines.append(line)

    return "\n\n".join(formatted_lines)
