"""
Some helper functions for sqlite.
"""

import os
import sqlite3
import time

import pandas as pd
from dagster import get_dagster_logger

MAX_RETRIES = 5
RETRY_DELAY = 1


def read_sql_sqlite(sql: str) -> pd.DataFrame:
    """
    Read data from SQLite with retry logic.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The result of the SQL query as a pandas DataFrame.
    """
    logger = get_dagster_logger()
    sqlite_path = os.environ.get("ANOMSTACK_SQLITE_PATH", "tmpdata/anomstack-sqlite.db")
    logger.info(f"sqlite_path: {sqlite_path}")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            conn = sqlite3.connect(sqlite_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return df
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                attempt += 1
                logger.warning(
                    f"Database is locked; attempt {attempt} of {MAX_RETRIES}. "
                    f"Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Error reading from SQLite: {e}")
                raise
        finally:
            if 'conn' in locals():
                conn.close()

    # If all retries fail, raise an error
    raise sqlite3.OperationalError("Database is locked after multiple attempts.")


def save_df_sqlite(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    """
    Save df to db with retry logic.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        table_key (str): The table name to save the DataFrame as.

    Returns:
        pd.DataFrame: The input DataFrame.
    """
    logger = get_dagster_logger()
    sqlite_path = os.environ.get("ANOMSTACK_SQLITE_PATH", "tmpdata/anomstack-sqlite.db")
    logger.info(f"sqlite_path: {sqlite_path}")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            conn = sqlite3.connect(sqlite_path)
            df.to_sql(table_key, conn, if_exists='append', index=False)
            conn.close()
            return df
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                attempt += 1
                logger.warning(
                    f"Database is locked; attempt {attempt} of {MAX_RETRIES}. "
                    f"Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Error saving DataFrame to SQLite: {e}")
                raise
    # If all retries fail, raise an error
    raise sqlite3.OperationalError("Database is locked after multiple attempts.")


def run_sql_sqlite(sql: str) -> None:
    """
    Execute a non-returning SQL statement in SQLite with retry logic.

    Args:
        sql (str): The SQL statement to execute.

    Returns:
        None
    """
    logger = get_dagster_logger()
    sqlite_path = os.environ.get("ANOMSTACK_SQLITE_PATH", "tmpdata/anomstack-sqlite.db")
    logger.info(f"sqlite_path: {sqlite_path}")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                attempt += 1
                logger.warning(
                    f"Database is locked; attempt {attempt} of {MAX_RETRIES}. "
                    f"Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Error executing SQL statement: {e}")
                raise
        finally:
            if 'conn' in locals():
                conn.close()

    # If all retries fail, raise an error
    raise sqlite3.OperationalError("Database is locked after multiple attempts.")
