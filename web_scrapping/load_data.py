import os
from web_scrapping.helpers.s3_helpers import s3_helper
from web_scrapping.utils.config import Config
config = Config.get_config()

def upload_to_s3(local_file_path):
    bucket_name = config["s3_bucket"]
    s3_key = os.path.basename(local_file_path)
    try:
        s3_helper.upload_file(local_file_path, s3_key)
        print(f"Uploaded {local_file_path} to S3 bucket {bucket_name} as {s3_key}")
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")

# Example usage:
final_directory = os.path.join(os.path.dirname(__file__), "processed_data.csv")
upload_to_s3(final_directory)