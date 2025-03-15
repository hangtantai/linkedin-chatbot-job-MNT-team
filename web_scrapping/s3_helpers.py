import os
import boto3
from typing import Optional
from botocore.exceptions import ClientError
from web_scrapping.logger import logger
class S3Helper:
    # Singleton pattern instance storage
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, bucket_name: str = None):
        """Initialize S3 client and bucket name"""
        # Lazy initialization - only set up once
        if not hasattr(self, "s3_client") or (bucket_name and self.bucket_name != bucket_name):
            self.s3_client = boto3.client('s3')
            # Only update bucket_name if provided and different from current
            if bucket_name:
                self.bucket_name = bucket_name
            elif not hasattr(self, "bucket_name"):
                self.bucket_name = None

    def upload_file(self, file_path: str, s3_key: Optional[str] = None) -> bool:
        """
        Upload a file to S3 bucket
        
        Args:
            file_path (str): Local path to the file
            s3_key (str, optional): The key (path) where the file will be stored in S3.
                                If not provided, uses the filename
        
        Returns:
            bool: True if file was uploaded successfully, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False

            # If s3_key not provided, use the filename
            if s3_key is None:
                s3_key = os.path.basename(file_path)

            self.s3_client.upload_file(
                Filename=file_path,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"Successfully uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            return False
    
    def read_file(self, key: str) -> str:
        """Read a file from s3 and return its content as string"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key = key)
            logger.info(f"Successfully read file from s3://{self.bucket_name}/{key}")
            return response["Body"].read().decode('utf-8')
        except Exception as e:
            logger.error(f"Unexpected error during S3 read: {str(e)}")
            return None
# Create singleton instance
s3_helper = S3Helper()