from abc import ABC, abstractmethod
import time
from typing import Optional, Any
class Command(ABC):
    """Base Command Interface"""

    def __init__(self):
        self.executed = False
        self.sucess = False
        self.start_time = None
        self.end_time = None
        self.error = None
        self.metadata = {}
    
    def validate(self) -> bool:
        """Validate command can be executed (optional override)"""
        return True

    def execute_with_logging(self) -> bool:
        """Execute with built-in logging and error handling"""
        if not self.validate():
            self.error = "Validation failed"
            return False
            
        self.start_time = time.time()
        try:
            result = self.execute()
            self.success = result
            return result
        except Exception as e:
            self.error = str(e)
            self.success = False
            return False
        finally:
            self.executed = True
            self.end_time = time.time()

    @abstractmethod
    def execute(self) -> None:
        """Execuate the command"""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command (if possible)"""
        pass

    def get_execution_time(self) -> Optional[float]:
        """Get execution time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
        
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the command"""
        self.metadata[key] = value