import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional
from web_scrapping.logger import Logger

logger = Logger()

class S3Helper:
    def __init__(self, bucket_name: str):
        """Initialize S3 client and bucket name"""
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

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