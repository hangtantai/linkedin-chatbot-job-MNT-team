import pandas as pd
import pymysql
import hashlib
import xxhash
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from web_scrapping.utils.logger import logger
from web_scrapping.utils.config import Config


# ================================
# General Configuration
# ================================
config = Config.get_config()
file_name  = config["job_data"]

host = config["host_aiven"]
port = config["port_aiven"]
user = config["user_aiven"]
password = config["password_aiven"]

# Database and table names for two cases:
db_name = "job_data"             # Original database: stores raw data
process_db_name = "process_data"  # Processed database: will calculate hash, parsed_time and perform deduplication
table_name = "job_data"           # Table for raw data
table_name_process = "job_data_process"  # Table for processed data

# ================================
# SQL connection and operation functions
# ================================

def connect_db_cloud_aiven(db_name: str, host: str, port: int, user: str, password: str) -> pymysql.connections.Connection:
    """
    Connect to the Aiven database and return the connection object.
    """

    connection = pymysql.connect(
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        db=db_name,
        host=host,
        password=password,
        port=port,
        user=user
    )
    return connection

def create_database(connection: pymysql.connections.Connection, db_name: str) -> None:
    """
    Drop if exists and create a new database.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`;")
        cursor.execute(f"CREATE DATABASE `{db_name}`;")
    connection.commit()
    logger.info(f"Database `{db_name}` has been created!")

def drop_table(connection: pymysql.connections.Connection, table_name: str) -> None:
    """
    Drop table if exists.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
    connection.commit()
    logger.info(f"Table `{table_name}` has been dropped (if existed)!")

def create_table(connection: pymysql.connections.Connection, db_name: str, table_name: str, include_parsed_time: bool = False) -> None:
    """
    Create table in the database.
    - If include_parsed_time=True: the table will have additional columns parsed_time (DATETIME type) and hash_value.
    - If False: the table will only contain the original columns (no hash_value, parsed_time).
    """
    with connection.cursor() as cursor:
        cursor.execute(f"USE `{db_name}`;")
        if include_parsed_time:
            table_def = f"""
                job_id INT AUTO_INCREMENT PRIMARY KEY,
                job_title VARCHAR(255),
                job_location VARCHAR(255),
                job_time_posted VARCHAR(255),
                job_applicants_applied TEXT,
                job_role VARCHAR(255),
                job_details TEXT,
                hash_value VARCHAR(64),
                parsed_time DATETIME
            """
        else:
            table_def = f"""
                job_id INT AUTO_INCREMENT PRIMARY KEY,
                job_title VARCHAR(255),
                job_location VARCHAR(255),
                job_time_posted VARCHAR(255),
                job_applicants_applied TEXT,
                job_role VARCHAR(255),
                job_details TEXT
            """
        cursor.execute(f"CREATE TABLE `{table_name}` ({table_def});")
    connection.commit()
    logger.info(f"Table `{table_name}` in database `{db_name}` has been created!")

def list_all_table_in_db(connection: pymysql.connections.Connection, db_name: str) -> None:
    """
    List all tables in the database.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"USE `{db_name}`;")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        logger.info(f"Tables in database `{db_name}`: {tables}")

def query_all_data_from_table(connection: pymysql.connections.Connection, db_name: str, table_name: str) -> None:
    """
    Query and print data from the table.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"USE `{db_name}`;")
        cursor.execute(f"SELECT * FROM `{table_name}`;")
        data = cursor.fetchall()
        logger.info(f"Data from table `{table_name}` in database `{db_name}`:")
        for record in data:
            logger.info(record)

def import_data_to_table(connection: pymysql.connections.Connection, db_name: str, table_name: str, df: pd.DataFrame) -> None:
    """
    Insert data from DataFrame into the table.
    The INSERT query will be selected based on the columns present in the DataFrame.
    """
    if df.empty:
        logger.info("No new data to import.")
        return
    with connection.cursor() as cursor:
        cursor.execute(f"USE `{db_name}`;")
        if "parsed_time" in df.columns and "hash_value" in df.columns:
            sql = f"""INSERT INTO `{table_name}` 
                      (job_title, job_location, job_time_posted, job_applicants_applied, job_role, job_details, hash_value, parsed_time)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
            values = df[["job_title", "job_location", "job_time_posted", "job_applicants_applied", "job_role", "job_details", "hash_value", "parsed_time"]].values.tolist()
        else:
            sql = f"""INSERT INTO `{table_name}` 
                      (job_title, job_location, job_time_posted, job_applicants_applied, job_role, job_details)
                      VALUES (%s, %s, %s, %s, %s, %s);"""
            values = df[["job_title", "job_location", "job_time_posted", "job_applicants_applied", "job_role", "job_details"]].values.tolist()
        cursor.executemany(sql, values)
    connection.commit()
    logger.info(f"{len(df)} new records have been added to table `{table_name}` in database `{db_name}`!")

def deduplicate_records_on_db(connection: pymysql.connections.Connection, db_name: str, table_name: str) -> None:
    """
    In the process_data database, remove duplicate records based on hash_value.
    Rule:
      - If multiple records have the same hash_value and parsed_time, keep only the record with the highest job_id.
      - If parsed_time is different, keep the record with the latest parsed_time.
    The query will delete records that meet the above conditions.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"USE `{db_name}`;")
        dedup_query = f"""
        DELETE t1 FROM `{table_name}` t1
        INNER JOIN `{table_name}` t2
            ON t1.hash_value = t2.hash_value
            AND (t1.parsed_time < t2.parsed_time OR 
                 (t1.parsed_time = t2.parsed_time AND t1.job_id < t2.job_id));
        """
        cursor.execute(dedup_query)
    connection.commit()
    logger.info("Deduplication on DB process_data has been completed!")

# ================================
# DataFrame processing functions (calculate hash and parsed_time columns)
# ================================

def generate_hash(job_title: str, job_location: str, job_role: str, job_details: str) -> str:
    """
    Calculate hash from job_title, job_location, job_role, and the first 200 characters of job_details.
    Handle missing values (NaN) safely.
    """
    job_details = job_details if isinstance(job_details, str) else ""  # Xử lý NaN thành chuỗi rỗng
    details_part = job_details[:200] if len(job_details) > 200 else job_details
    combined = f"{job_title}-{job_location}-{job_role}-{details_part}"
    return xxhash.xxh64(combined).hexdigest()


def parse_relative_time(time_str: str, now: datetime = None) -> datetime:
    """
    Convert a time description string (e.g., "2 weeks ago", "Reposted 20 hours ago")
    into a datetime object. If parsing fails, return the current time.
    """
    if now is None:
        now = datetime.now()
    s = time_str.lower().strip().replace("reposted", "").strip()
    pattern = r"(\d+)\s+(month|months|week|weeks|day|days|hour|hours)\s+ago"
    match = re.search(pattern, s)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit.startswith("month"):
            return now - relativedelta(months=num)
        elif unit.startswith("week"):
            return now - relativedelta(weeks=num)
        elif unit.startswith("day"):
            return now - relativedelta(days=num)
        elif unit.startswith("hour"):
            return now - relativedelta(hours=num)
    return now

def renumber_ids_on_db(connection: pymysql.connections.Connection, db_name: str, table_name: str) -> None:
    """
    Renumber job_id for the table, so that the job_ids are continuously numbered in ascending order.
    Then, reset AUTO_INCREMENT to 1.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"USE `{db_name}`;")
        # Initialize counter variable
        cursor.execute("SET @new_id = 0;")
        # Update job_id according to the current order of job_id
        cursor.execute(f"UPDATE `{table_name}` SET job_id = (@new_id := @new_id + 1) ORDER BY job_id;")
        # Reset AUTO_INCREMENT for the table
        cursor.execute(f"ALTER TABLE `{table_name}` AUTO_INCREMENT = 1;")
    connection.commit()
    logger.info(f"IDs in table `{table_name}` of database `{db_name}` have been renumbered!")

# ================================
# Main part: Data processing and insertion into two databases
# ================================

def main():
    # Read data from CSV (raw data)
    df = pd.read_csv(file_name)
    logger.info("Raw data from CSV:")
    logger.info(df)

    # Calculate hash_value and parsed_time on DataFrame
    # Note: Here only calculate for process_data, not used in job_data
    df["hash_value"] = df.apply(
        lambda row: generate_hash(
            row["job_title"],
            row["job_location"],
            row["job_role"],
            row["job_details"]
        ), axis=1
    )
    df["parsed_time"] = df["job_time_posted"].apply(lambda x: parse_relative_time(x))
    df = df.fillna("")
    # ------------------------------
    # Part 1: Processing for job_data database (raw)
    # ------------------------------
    logger.info("--- Processing for job_data database ---")
    # For job_data, insert raw data WITHOUT hash_value and parsed_time
    conn = connect_db_cloud_aiven(db_name, host, port, user, password)
    create_database(conn, db_name)
    conn = connect_db_cloud_aiven(db_name, host, port, user, password)
    create_table(conn, db_name, table_name, include_parsed_time=False)
    df_raw = df.drop(columns=["parsed_time", "hash_value"])
    conn = connect_db_cloud_aiven(db_name, host, port, user, password)
    import_data_to_table(conn, db_name, table_name, df_raw)
    conn = connect_db_cloud_aiven(db_name, host, port, user, password)
    list_all_table_in_db(conn, db_name)
    query_all_data_from_table(conn, db_name, table_name)
    conn.close()

    # ------------------------------
    # Part 2: Processing for process_data database (deduplication)
    # ------------------------------
    logger.info("--- Processing for process_data database (deduplication) ---")
    # Create process_data database and DROP table if exists to ensure new schema with parsed_time and hash_value
    conn = connect_db_cloud_aiven(process_db_name, host, port, user, password)
    create_database(conn, process_db_name)
    conn = connect_db_cloud_aiven(process_db_name, host, port, user, password)
    drop_table(conn, table_name_process)
    create_table(conn, process_db_name, table_name_process, include_parsed_time=True)
    conn.close()
    
    # Insert all data (including hash_value and parsed_time) into process_data
    conn = connect_db_cloud_aiven(process_db_name, host, port, user, password)
    import_data_to_table(conn, process_db_name, table_name_process, df)
    conn.close()
    
    # After insertion, perform deduplication on the process_data DB:
    # Remove duplicate records: keep the record with the latest parsed_time (or if equal, the one with the higher job_id)
    conn = connect_db_cloud_aiven(process_db_name, host, port, user, password)
    deduplicate_records_on_db(conn, process_db_name, table_name_process)
    #renumber_ids_on_db(conn, process_db_name, table_name_process)
    conn = connect_db_cloud_aiven(process_db_name, host, port, user, password)
    list_all_table_in_db(conn, process_db_name)
    query_all_data_from_table(conn, process_db_name, table_name_process)
    conn.close()

main()