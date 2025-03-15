from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ExtractorStrategy(ABC):
    """Base strategy interface for data extraction"""
    
    @abstractmethod
    def extract(self, source: str) -> Any:
        """
        Extract data from a source
        
        Args:
            source: The source to extract data from (typically a file path)
            
        Returns:
            Extracted data in the appropriate format
        """
        pass