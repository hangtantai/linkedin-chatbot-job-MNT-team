# from web_scrapping.s3_helpers import S3Helper
# import streamlit as st
# import os

# bucket_name = st.secrets["S3_BUCKET_JOB"]
# s3_helper = S3Helper(bucket_name)

# # Test upload
# # link_file = os.path.join(os.path.dirname(__file__), 'output.txt')
# # s3_helper.upload_file(link_file, "test.txt")

# # Test read
# content = s3_helper.read_file("job_data.csv")
# print(content)

from web_scrapping.utils.config import Config

config = Config.get_config()
email = config["email"]
print(email)
