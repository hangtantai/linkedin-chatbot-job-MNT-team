import logging 
import os
from datetime import datetime
from typing import Optional

class Logger:
    # what is called?
    _instance = None

    # what is that? cls?
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "logger"):
            # why need to do it?
            self.logger = logging.getLogger("linkedin_scapper")
            self._setup_logger()
    
    def _setup_logger(self):
        """Set up logging configuration"""
        # what is that?
        self.logger.setLevel(logging.INFO)
        
        # Creates logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True) # what is attribute exist_ok ?
    
        # File handler with current date
        log_file = os.path.join(log_dir, f"scrapper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO) # why need to set level?
        
        # Console handler, why need console?
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) # why need to set level?
        
        # Set formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter) # why need to set format
        console_handler.setFormatter(formatter) # why need to set format
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Log error level message"""
        self.logger.info(message, extra = extra) # what is extra?
    
    def error(self, message:str, extra: Optional[dict] = None):
        """Log error level message"""
        self.logger.error(message, extra = extra)
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """Log warning level message"""
        self.logger.warning(message, extra = extra)

    def debug(self, message: str, extra: Optional[dict] = None):
        """Log debug level message"""
        self.logger.debug(message, extra = extra)

# Create a singleton instance
logger = Logger()
# what is singleton instancce? why need to use it?