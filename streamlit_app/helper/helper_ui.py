# Helper function to escape special characters
def escape_for_js(text: str) -> str:
    """
    Escape special characters for JavaScript string.
    
    Args:
        text (str): The text to escape.
    """
    return text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')
