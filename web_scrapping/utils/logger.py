import os
import logging 
from datetime import datetime
from typing import Optional

class Logger:
    # instance storage: private class variable stores the single instance
    _instance = None

    # overiding method
    def __new__(cls, *args, **kwargs): # cls: class itself (Logger)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    # lazy initialization
    def __init__(self):
        if not hasattr(self, "logger"):
            # Create a logger instance 
            self.logger = logging.getLogger("linkedin_scapper")
            self._setup_logger()
    
    def _setup_logger(self):
        """Set up logging configuration"""
        # level in logger: DEBUG < INFO < WARNING < ERROR < CRITICAL
        # set minimum severity level for this logger to process message -> DEBUG will be ignored
        self.logger.setLevel(logging.INFO)
        
        # Creates logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True) # prevents errors if the directory already exists
    
        # File handler with current date
        log_file = os.path.join(log_dir, f"scrapper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file) # write a log message to this file
        file_handler.setLevel(logging.INFO) 
        
        # Console handler
        console_handler = logging.StreamHandler() # send log messgae to the console (terminal)
        console_handler.setLevel(logging.INFO)
        
        # Set formatter, format for file log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Log error level message"""
        self.logger.info(message, extra = extra)
    
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
# create a variable logger that holds the singleton instance
# just declare variable for another file rather than the Logger class directly
logger = Logger()