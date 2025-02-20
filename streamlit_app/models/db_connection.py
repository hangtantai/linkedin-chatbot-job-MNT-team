# Utilization
import pandas as pd
# Aiven CLoud
import pymysql
import os
from typing import Generator
import sys
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

from streamlit_app.config.config import Config
config = Config()
DB_config = config.get_config()["DB_config"]

class Database:
    def __init__(self):
        self.connection = None
        self.db_name = os.environ.get("DB_AIVEN")
        self.table_name = os.environ.get("TABLE_AIVEN")
        self.db_config = DB_config
        self.batch_size = 1000

    def open_connection(self) -> pymysql.Connection:
        """
        Establish a connection to the database

        Returns:
            connection: A connection object to the database.
        """
        try:
            self.connection = pymysql.connect(**self.db_config)
            print("Database connection established!")
            return self.connection
        except pymysql.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    def close_connection(self):
        """
        Close the database connection.

        Args:
            connection (pymysql.Connection): A connection object to the database.
        """
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
            self.connection = None

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch data from the database using the provided query.

        Args:
            connection (pymysql.Connection): A connection object to the database.
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched data.
        """
        if not self.connection:
            print("No active connection. Opening connection ...")
            self.connection = self.open_connection()
            print(self.connection)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.db_name}.{self.table_name}")
                df = cursor.fetchall()
                return df if df else None
        except pymysql.Error as e:
            print(f"Error fetching data from the database: {e}")
            return None
        finally:
            self.close_connection()

    def fetch_large_dataset(self, query: str) -> Generator[list, None, None]:
        """
        Fetch data from the database using the provided query.

        Args:
            connection (pymysql.Connection): A connection object to the database.
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched data.
        """
        if not self.connection:
            print("No active connection. Opening connection ...")
            self.connection = self.open_connection()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.db_name}.{self.table_name}")
                while True:
                    rows = cursor.fetchmany(self.batch_size)
                    if not rows:
                        break
                    yield rows
        except pymysql.Error as e:
            print(f"Error fetching data from the database: {e}")
            return None
        finally:
            self.close_connection()