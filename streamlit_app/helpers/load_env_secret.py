import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional, Union

def get_env_var(key: str, secrets_path: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable from secrets.toml or OS environment
    
    Args:
        key (str): The key to look for
        secrets_path (str, optional): Path to secrets.toml file
        
    Returns:
        Optional[str]: The value if found, None otherwise
    """
    # Try to load from secrets.toml first
    if not secrets_path:
        project_root = Path(__file__).parent.parent.parent
        secrets_path = os.path.join(project_root, 'streamlit_app', '.streamlit', 'secrets.toml')
    
    try:
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            if key in secrets:
                return secrets[key]
    except Exception as e:
        print(f"Error loading secrets file: {str(e)}")
    
    # # Fallback to environment variables
    # env_value = os.getenv(key)
    # if env_value:
    #     return env_value
        
    # print(f"Warning: No value found for key {key}")
    # return None