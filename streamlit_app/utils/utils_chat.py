from typing import List, Dict, Any

def count_tokens(encoding , text: str) -> int:
    """
    Count the number of tokens in a message
    
    Args:
        message (str): Input message
    
    Returns:
        int: Number of tokens
    """
    return len(encoding.encode(text))

def check_token_limit(max_tokens: int, encoding: Any,  messages: List[Dict[str, str]]) -> bool:
    """
    Check if the combined messages exceed token limit
    
    Args:
        messages (List[Dict[str, str]]): List of message dictionaries
        
    Returns:
        bool: True if within limit, False if exceeds
    """
    total_tokens = sum(count_tokens(encoding, msg["content"]) for msg in messages)

    return total_tokens <= max_tokens

def format_messages_for_model(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Format messages for model input
    
    Args:
        messages (List[Dict[str, str]]): Raw messages from chat history
    
    Returns:
        List[Dict[str, str]]: Formatted messages for model
    """
    return [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in messages
    ]

def validate_message(message: str) -> bool:
    """
    Validate user message
    
    Args:
        message (str): User input message
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not message or not message.strip():
        return False
    return True


@staticmethod
def create_message(role: str, content: str) -> Dict[str, str]:
    """
    Create a message dictionary
    
    Args:
        role (str): Message role (user/assistant)
        content (str): Message content
    
    Returns:
        Dict[str, str]: Formatted message dictionary
    """
    return {
        "role": role,
        "content": content
        }