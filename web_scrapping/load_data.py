# import necessary library
import pandas as pd
import pymysql
import os
from web_scrapping.load_env import load_env_file
load_env_file(env_filename=".env", app_folder="web_scrapping")

# define variables
file_name = "job_data.csv"
host = os.environ["HOST"]
port = os.environ["PORT"]
db_name = os.environ["DB_NAME"]
user = os.environ["USER"]
password = os.environ["PASSWORD"]
table_name = os.environ["TABLE_NAME"]

def read_csv(file_name: str) -> pd.DataFrame:
    """
    Read csv file and return DataFrame type

    Args:
        file_name (str): file name of csv file
    
    Returns:
        pd.DataFrame: DataFrame type of csv file
    """
    df = pd.read_csv(file_name)
    return df

def connect_db_cloud_aiven(db_name: str, host: str, port: int, user: str, password: str) -> pymysql.connect:
    """
    Connect to cloud database using Aiven

    Args:
        db_name (str): database name
        host (str): host of database
        port (int): port of database
        user (str): user of database
        password (str): password of database
    
    Returns:
        pymysql.connect: connection to database
    """
    # set default timeout
    timeout = 10

    # set up connection
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=db_name,
        host=host,
        password=password,
        read_timeout=timeout,
        port=port,
        user=user,
        write_timeout=timeout,
    )
    return connection

def create_database(connection: pymysql.connect, db_name: str) -> None:
    """
    Create database in aiven cloud

    Args:
        connection (pymysql.connect): connection to database
        db_name (str): database name
    
    Returns:
        None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
        cursor.execute(f"CREATE DATABASE {db_name};")
        cursor.connection.commit()
    finally:
        connection.close()

def create_table(connection: pymysql.connect, db_name: str, table_name: str) -> None:
    """
    Create table in aiven cloud

    Args:
        connection (pymsql.connect): connection to database
        db_name (str): database name
        table_name (str): table name
    
    Returns:
        None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name};")
        cursor.execute(
            f"CREATE TABLE {table_name} ("
            "job_id INT AUTO_INCREMENT,"
            "job_title VARCHAR(255),"
            "job_location VARCHAR(255),"
            "job_time_posted VARCHAR(255),"
            "job_applicants_applied TEXT,"
            "job_role VARCHAR(255),"
            "job_details TEXT,"
            "PRIMARY KEY (job_id)"
            ");"
        )
        cursor.connection.commit()
    finally:
        connection.close()

def list_all_table_in_db(connection: pymysql.connect, db_name: str) -> None:
    """
    List all tables in database

    Args:
        connection (pymysql.connect): connection to database
        db_name (str): database name
    
    Returns:
        None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name};")
        cursor.execute("SHOW TABLES;")
        print(cursor.fetchall())
    finally:
        connection.close()

def import_data_to_table(connection: pymysql.connect, db_name: str, table_name: str, df: pd.DataFrame) -> None:
    """
    Import data to table in database
    
    Args:
        connection (pymysql.connect): connection to database
        db_name (str): database name
        table_name (str): table name
        df (pd.DataFrame): DataFrame type of data
    
    Returns:
        None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name};")
        cursor.executemany(
            f"INSERT INTO {table_name} (job_title, job_location, job_time_posted, job_applicants_applied, job_role, job_details) VALUES (%s, %s, %s, %s, %s, %s);",
            df.values.tolist(),
        )
        cursor.connection.commit()
    finally:
        connection.close()

def query_all_data_from_table(connection: pymysql.connect, db_name: str, table_name: str) -> None:
    """
    Query data from table in database

    Args:
        connection (pymysql.connect): connection to database
        db_name (str): database name
        table_name (str): table name
    
    Returns:
        None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name};")
        cursor.execute(f"SELECT * FROM {table_name};")
        print(cursor.fetchall())
    finally:
        connection.close()

def get_all_columns_from_table(connection: pymysql.connect, db_name: str, table_name: str) -> None:
    """
    Get all columns from table in database

    Args:
        connection (pymysql.connect): connection to database
        db_name (str): database name
        table_name (str): table name
    
    Returns:
        None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name};")
        cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        print(cursor.fetchall())
    finally:
        connection.close()

def query_search_data_from_table(connection: pymysql.connect, db_name: str, table_name: str, search: str) -> None:
    """
    Query data from table in database

    Args:
        connection (pymysql.connect): connection to database
        db_name (str): database name
        table_name (str): table name
        search (str): search query
    
    Returns:
        None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name};")
        cursor.execute(f"SELECT * FROM {table_name} WHERE job_title LIKE '%{search}%';")
        print(cursor.fetchall())
    finally:
        connection.close()

def main():

    # read csv file
    df = read_csv(file_name)

    # intialize connection
    connection = connect_db_cloud_aiven(db_name, host, port, user, password)

    # create database
    create_database(connection, db_name)

    # create table
    create_table(connection, db_name, table_name)

    # list all table to check if table is created
    list_all_table_in_db(connection, db_name)

    # import data into table
    import_data_to_table(connection, db_name, table_name, df)

    # query all data
    query_all_data_from_table(connection, db_name, table_name)

main()