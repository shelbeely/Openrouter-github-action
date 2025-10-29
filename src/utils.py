# src/utils.py

def is_thin_content(content: str) -> bool:
    """
    Checks if the given content is too thin to be useful.
    """
    return len(content.split()) < 10
