"""
Some helper functions for duckdb.
"""

import os
from typing import Union

import pandas as pd
from dagster import get_dagster_logger
from duckdb import connect, query


def read_sql_duckdb(sql: str) -> pd.DataFrame:
    """
    Read data from SQL.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The result of the SQL query as a pandas DataFrame.
    """

    logger = get_dagster_logger()

    duckdb_path = os.environ.get("ANOMSTACK_DUCKDB_PATH", "tmpdata/anomstack-duckdb.db")
    logger.info(f"duckdb_path:{duckdb_path}")

    if duckdb_path.startswith("md:"):
        motherduck_token = os.environ.get("ANOMSTACK_MOTHERDUCK_TOKEN", None)
        duckdb_path = duckdb_path + f"?motherduck_token={motherduck_token}"
    else:
        os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)

    conn = connect(duckdb_path)
    df = query(connection=conn, query=sql).df()

    return df


def save_df_duckdb(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    """
    Save df to db.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        table_key (str): The table name to save the DataFrame as.

    Returns:
        pd.DataFrame: The input DataFrame.
    """

    logger = get_dagster_logger()

    duckdb_path = os.environ.get("ANOMSTACK_DUCKDB_PATH", "tmpdata/anomstack-duckdb.db")
    logger.info(f"duckdb_path:{duckdb_path}")

    if duckdb_path.startswith("md:"):
        motherduck_token = os.environ.get("ANOMSTACK_MOTHERDUCK_TOKEN", None)
        duckdb_path = duckdb_path + f"?motherduck_token={motherduck_token}"
    else:
        os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)

    conn = connect(duckdb_path)

    try:
        if "." in table_key:
            schema, _ = table_key.split(".")
            query(connection=conn, query=f"CREATE SCHEMA IF NOT EXISTS {schema}")
        query(connection=conn, query=f"INSERT INTO {table_key} SELECT * FROM df")
    except Exception:
        query(connection=conn, query=f"CREATE TABLE {table_key} AS SELECT * FROM df")

    return df


def run_sql_duckdb(sql: str, return_df: bool = False) -> Union[pd.DataFrame, None]:
    """
    Execute a non-returning SQL statement in DuckDB.

    Args:
        sql (str): The SQL statement to execute.
        return_df (bool, optional): Whether to return results as a DataFrame. Defaults to False.

    Returns:
        pd.DataFrame or None: If return_df is True, returns the query results as a DataFrame.
            Otherwise returns None.
    """
    logger = get_dagster_logger()

    duckdb_path = os.environ.get("ANOMSTACK_DUCKDB_PATH", "tmpdata/anomstack-duckdb.db")
    logger.info(f"duckdb_path: {duckdb_path}")

    if duckdb_path.startswith("md:"):
        motherduck_token = os.environ.get("ANOMSTACK_MOTHERDUCK_TOKEN", None)
        duckdb_path = duckdb_path + f"?motherduck_token={motherduck_token}"
    else:
        os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)

    conn = connect(duckdb_path)

    try:
        if return_df:
            df = query(connection=conn, query=sql).df()
            
            return df
        
        else:
            query(connection=conn, query=sql)
    
    except Exception as e:
        logger.error(f"Error executing SQL statement in DuckDB: {e}")
        raise
    
    finally:
        conn.close()
