import os
import sys
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
from streamlit_app.utils.logger import logger
from streamlit_app.utils.config import Config
from streamlit_app.utils.utils_chat import (
    count_tokens,
    check_token_limit,
    format_messages_for_model,
    create_message,
)

__all__ = [
    "logger",
    "Config",
    "count_tokens",
    "check_token_limit",
    "format_messages_for_model",
    "create_message"
]