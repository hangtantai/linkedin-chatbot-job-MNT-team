from pathlib import Path
import os
from dotenv import load_dotenv
from typing import Optional

def load_env_file(env_filename: str = ".env", app_folder: Optional[str] = None) -> None:
    """
    Load environment variables from a specified .env file
    
    Args:
        env_filename (str): Name of the environment file (default: .env)
        app_folder (str, optional): Subfolder name where the .env file is located
    """
    # Get project root (3 levels up from utils folder)
    project_root = Path(__file__).parent.parent.parent
    
    # Construct path to .env file
    if app_folder:
        env_path = os.path.join(project_root, app_folder, env_filename)
    else:
        env_path = os.path.join(project_root, env_filename)
    
    # Load environment variables
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
    else:
        raise FileNotFoundError(f"Environment file not found: {env_path}")