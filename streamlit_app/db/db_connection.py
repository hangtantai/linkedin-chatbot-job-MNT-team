# # Utilization
# import pandas as pd
# import pymysql
# import os
# import sys
# import streamlit as st
# from typing import Generator
# # Check if running on Streamlit Cloud
# if "mnt" in os.getcwd():
#     os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
#     sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

# # import external file
# from streamlit_app.utils.config import Config
# from streamlit_app.utils.logger import logger

# # Variables
# config = Config().get_config()
# DB_config = config["DB_config"]
# db_name = st.secrets["DB_AIVEN"]
# table_name = st.secrets["TABLE_AIVEN"]
# batch_size = config["batch_size"]
# class Database:
#     """
#     Connection to Aiven database (MySQL)
#     Args:
#     Args:
#         DB_config: based on requirement param to connect
#     """
#     def __init__(self):
#         self.connection = None
#         self.db_name = db_name
#         self.table_name = table_name
#         self.db_config = DB_config
#         self.batch_size = batch_size

#     def open_connection(self) -> pymysql.Connection:
#         """
#         Establish a connection to the database

#         Returns:
#             connection: A connection object to the database.
#         """
#         try:
#             self.connection = pymysql.connect(**self.db_config)
#             logger.info(f"Database connection established!")
#             return self.connection
#         except pymysql.Error as e:
#             logger.error(f"Error connecting to the database: {e}")
#             raise

#     def close_connection(self) -> None:
#         """
#         Close the database connection.

#         Args:
#             connection (pymysql.Connection): A connection object to the database.
#         """
#         try:
#             if self.connection:
#                 self.connection.close()
#                 logger.info("Database connection closed.")
#                 self.connection = None
#         except Exception as e:
#             logger.error(f"Error closing the database connection {str(e)}")
#             raise

#     def fetch_data(self) -> pd.DataFrame:
#         """
#         Fetch data from the database using the provided query.

#         Args:
#             connection (pymysql.Connection): A connection object to the database.
#             query (str): The SQL query to execute.

#         Returns:
#             pd.DataFrame: A DataFrame containing the fetched data.
#         """
#         if not self.connection:
#             logger.info("No active connection. Opening connection ...")
#             self.connection = self.open_connection()
#             logger.info(self.connection)

#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(f"SELECT * FROM {self.db_name}.{self.table_name}")
#                 df = cursor.fetchall()
#                 logger.info("Featching all data successfully.")
#                 return df if df else None
#         except pymysql.Error as e:
#             logger.error(f"Error fetching data from the database: {e}")
#             return None
#         finally:
#             self.close_connection()

#     def fetch_large_dataset(self) -> Generator[list, None, None]:
#         """
#         Fetch data from the database using the provided query.

#         Args:
#             connection (pymysql.Connection): A connection object to the database.
#             query (str): The SQL query to execute.

#         Returns:
#             pd.DataFrame: A DataFrame containing the fetched data.
#         """
#         if not self.connection:
#             logger.info("No active connection. Opening connection ...")
#             self.connection = self.open_connection()

#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(f"SELECT * FROM {self.db_name}.{self.table_name}")
#                 while True:
#                     rows = cursor.fetchmany(self.batch_size)
#                     if not rows:
#                         break
#                     logger.info("Featching large dataset successfully.")
#                     yield rows
#         except pymysql.Error as e:
#             logger.error(f"Error fetching data from the database: {e}")
#             return None
#         finally:
#             self.close_connection()