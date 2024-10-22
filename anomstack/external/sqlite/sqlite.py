"""
Some helper functions for sqlite.
"""

import os
import sqlite3

import pandas as pd
from dagster import get_dagster_logger


def read_sql_sqlite(sql: str) -> pd.DataFrame:
    """
    Read data from SQL.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The result of the SQL query as a pandas DataFrame.
    """

    logger = get_dagster_logger()

    sqlite_path = os.environ.get("ANOMSTACK_SQLITE_PATH", "tmpdata/anomstack.db")
    logger.info(f"sqlite_path:{sqlite_path}")

    conn = sqlite3.connect(sqlite_path)

    logger.debug(f"sql:\n{sql}")
    df = pd.read_sql_query(sql, conn)
    logger.debug(f"df:\n{df}")

    conn.close()
    return df


def save_df_sqlite(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    """
    Save df to db.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        table_key (str): The table name to save the DataFrame as.

    Returns:
        pd.DataFrame: The input DataFrame.
    """

    logger = get_dagster_logger()

    sqlite_path = os.environ.get("ANOMSTACK_SQLITE_PATH", "tmpdata/anomstack.db")
    logger.info(f"sqlite_path:{sqlite_path}")
    conn = sqlite3.connect(sqlite_path)

    try:
        df.to_sql(table_key, conn, if_exists='append', index=False)
    except Exception as e:
        logger.error(f"Error saving DataFrame to SQLite: {e}")
        raise

    conn.close()
    return df
