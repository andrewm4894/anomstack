"""
Some helper functions for sqlite.
"""

import os
import libsql_experimental as libsql
import time

import pandas as pd
from dagster import get_dagster_logger
from anomstack.df.utils import generate_insert_sql

MAX_RETRIES = 5
RETRY_DELAY = 1


def get_conn(sqlite_path: str) -> libsql.Connection:
    """
    Get a connection to the SQLite database.

    Args:
        sqlite_path (str): The path to the SQLite database.

    Returns:
        libsql.Connection: The connection object.
    """
    if sqlite_path.endswith('turso.io'):
        url = os.environ.get("ANOMSTACK_TURSO_DATABASE_URL", None)
        auth_token = os.environ.get("ANOMSTACK_TURSO_AUTH_TOKEN", None)
        conn = libsql.connect(sqlite_path, sync_url=url, auth_token=auth_token)
    else:
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        conn = libsql.connect(sqlite_path)    
    return conn


def infer_sqlite_type(dtype):
    """Map pandas dtypes to SQLite types."""
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "REAL"
    elif pd.api.types.is_string_dtype(dtype):
        return "TEXT"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TEXT"
    else:
        return "TEXT"


def generate_create_table_sql(df, table_name) -> str:
    """Generate SQL DDL and batched DML from DataFrame."""
    # Infer column types for CREATE TABLE
    column_defs = [
        f"{col} {infer_sqlite_type(dtype)}"
        for col, dtype in zip(df.columns, df.dtypes)
    ]
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)});"
    return create_table_sql


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
    
    if not sqlite_path.endswith('turso.io'):
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            conn = get_conn(sqlite_path)
            df = pd.read_sql_query(sql, conn)
            return df
        except Exception as e:
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

    # If all retries fail, raise an error
    raise Exception("Database is locked after multiple attempts.")


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
    
    if not sqlite_path.endswith('turso.io'):
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            conn = get_conn(sqlite_path)
            create_table_sql = generate_create_table_sql(df, table_key)
            insert_sqls = generate_insert_sql(df, table_key)
            conn.execute(create_table_sql)
            for sql in insert_sqls:
                conn.execute(sql)
            conn.commit()
            return df
        except Exception as e:
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
    raise Exception("Database is locked after multiple attempts.")


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
    
    if not sqlite_path.endswith('turso.io'):
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            conn = get_conn(sqlite_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            return
        except Exception as e:
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
    raise Exception("Database is locked after multiple attempts.")
