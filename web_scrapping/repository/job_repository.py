import pandas as pd
from web_scrapping.utils.logger import logger

class JobRepository:
    """Repository for job data persistence operations"""
    
    def __init__(self, file_path, s3_helper):
        """
        Initialize the repository
        
        Args:
            file_path: Local file path for job data
            s3_helper: S3Helper instance for cloud storage
        """
        self.file_path = file_path
        self.s3_helper = s3_helper
        
    def save(self, data):
        """
        Save job data to local CSV file
        
        Args:
            data: DataFrame containing job data
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not data.empty:
            data.to_csv(self.file_path, index=False)
            logger.info(f"Successfully saved job data to {self.file_path}")
            return True
        logger.warning("No job data to save")
        return False
    
    def upload_to_s3(self, s3_key):
        """
        Upload job data to S3
        
        Args:
            s3_key: S3 object key/path
            
        Returns:
            bool: True if uploaded successfully, False otherwise
        """
        success = self.s3_helper.upload_file(self.file_path, s3_key)
        if success:
            logger.info(f"Successfully uploaded job data to S3 with key: {s3_key}")
        else:
            logger.error(f"Failed to upload job data to S3 with key: {s3_key}")
        return success