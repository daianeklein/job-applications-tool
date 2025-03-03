import re
import sys
import os
from pathlib import Path
from unidecode import unidecode

# Define paths
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

# Import job description and prompt
sys.path.insert(0, str(parent_dir / "prompts"))
from job_description import job_description_text


def clean_docstring(docstring: str) -> str:
    """
    Replaces special characters with their closest ASCII equivalents 
    and removes emojis from a given docstring.

    Args:
        docstring (str): The input docstring.

    Returns:
        str: The cleaned docstring.
    """
    # Remove emojis using a regex pattern that detects Unicode emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric symbols
        "\U0001F800-\U0001F8FF"  # Supplemental symbols
        "\U0001F900-\U0001F9FF"  # Additional emojis
        "\U0001FA00-\U0001FA6F"  # Symbols and pictographs
        "\U0001FA70-\U0001FAFF"  # More symbols
        "]+", flags=re.UNICODE
    )

    # Remove emojis
    docstring = emoji_pattern.sub("", docstring)

    # Convert special characters to their ASCII equivalents
    docstring = unidecode(docstring)

    return docstring

if __name__ == "__main__":
    clean_docstring(job_description_text)
