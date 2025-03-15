from web_scrapping.strategies.extractor_strategy import ExtractorStrategy
from web_scrapping.strategies.link_extractor_strategy import LinkExtractorStrategy
from web_scrapping.strategies.detail_extractor_strategy import DetailExtractorStrategy

class ExtractorFactory:
    """Factory to create different extractor strategies"""
    
    @staticmethod
    def create_extractor(extractor_type: str) -> ExtractorStrategy:
        """
        Create a specific extractor strategy
        
        Args:
            extractor_type: Type of extractor ('link' or 'detail')
            
        Returns:
            Concrete ExtractorStrategy instance
            
        Raises:
            ValueError: If extractor_type is not recognized
        """
        if extractor_type.lower() == "link":
            return LinkExtractorStrategy()
        elif extractor_type.lower() == "detail":
            return DetailExtractorStrategy()
        else:
            raise ValueError(f"Unknown extractor type: {extractor_type}")