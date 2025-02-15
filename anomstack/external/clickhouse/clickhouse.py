"""
Some helper functions for ClickHouse using clickhouse-connect.
"""

import os
import pandas as pd
from dagster import get_dagster_logger
from clickhouse_connect import get_client


def map_dtype(dtype) -> str:
    """
    Map a Pandas dtype to a ClickHouse data type.
    """
    if pd.api.types.is_integer_dtype(dtype):
        return "Int64"
    elif pd.api.types.is_float_dtype(dtype):
        return "Float64"
    elif pd.api.types.is_bool_dtype(dtype):
        return "UInt8"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "DateTime"
    else:
        return "String"


def get_clickhouse_client():
    """
    Create a ClickHouse client using environment variables for connection parameters.

    Returns:
        ClickHouseClient: Configured ClickHouse client instance
    """
    logger = get_dagster_logger()

    host = os.environ.get("ANOMSTACK_CLICKHOUSE_HOST", "localhost")
    port = int(os.environ.get("ANOMSTACK_CLICKHOUSE_PORT", "8123"))
    user = os.environ.get("ANOMSTACK_CLICKHOUSE_USER", "anomstack")
    password = os.environ.get("ANOMSTACK_CLICKHOUSE_PASSWORD", "anomstack")
    database = os.environ.get("ANOMSTACK_CLICKHOUSE_DATABASE", "default")

    logger.info(f"ClickHouse connection: {host}:{port}/{database}")

    return get_client(
        host=host, 
        port=port, 
        username=user, 
        password=password, 
        database=database
    )


def read_sql_clickhouse(sql: str) -> pd.DataFrame:
    """
    Read data from ClickHouse using an SQL query.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The result of the SQL query as a pandas DataFrame.
    """
    client = get_clickhouse_client()
    result = client.query(sql)
    
    return pd.DataFrame(result.result_set, columns=result.column_names)


def save_df_clickhouse(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    """
    Save a Pandas DataFrame to ClickHouse.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        table_key (str): The table name to save the DataFrame as.

    Returns:
        pd.DataFrame: The input DataFrame.
    """
    client = get_clickhouse_client()
    # Convert the DataFrame to a list of rows and extract column names.
    data = df.values.tolist()
    columns = list(df.columns)

    try:
        client.insert(table=table_key, data=data, column_names=columns)
    except Exception as e:
        logger = get_dagster_logger()
        logger.info(
            f"Table {table_key} may not exist. Attempting to create table. Error: {e}"
        )
        # Construct a CREATE TABLE statement based on the DataFrame schema.
        columns_defs = []
        for col, dtype in df.dtypes.items():
            ch_type = map_dtype(dtype)
            # Use backticks around column names in case of reserved words.
            columns_defs.append(f"`{col}` {ch_type}")
        columns_str = ", ".join(columns_defs)
        create_sql = (
            f"CREATE TABLE IF NOT EXISTS {table_key} ({columns_str}) "
            "ENGINE = MergeTree() ORDER BY tuple()"
        )
        client.command(create_sql)
        # Insert the data after creating the table.
        client.insert(table=table_key, data=data, column_names=columns)

    return df


def run_sql_clickhouse(sql: str) -> None:
    """
    Execute a non-returning SQL statement in ClickHouse.

    Args:
        sql (str): The SQL statement to execute.

    Returns:
        None
    """
    client = get_clickhouse_client()
    try:
        client.command(sql)
    except Exception as e:
        logger = get_dagster_logger()
        logger.error(f"Error executing SQL statement in ClickHouse: {e}")
        raise
