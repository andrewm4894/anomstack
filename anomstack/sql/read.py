"""
This module provides functions for reading data from SQL databases using different database connectors.
"""

import pandas as pd
from dagster import get_dagster_logger

from anomstack.external.duckdb.duckdb import read_sql_duckdb
from anomstack.external.gcp.bigquery import read_sql_bigquery
from anomstack.external.snowflake.snowflake import read_sql_snowflake


def db_translate(sql: str, db: str) -> str:
    """
    Replace some functions with their db-specific equivalents.

    Args:
        sql (str): The SQL query to be translated.
        db (str): The name of the database to which the query will be sent.

    Returns:
        str: The translated SQL query.
    """
    if db == "bigquery":
        sql = sql.replace("now()", "current_timestamp()")
    elif db == "snowflake":
        sql = sql.replace("now()", "current_timestamp()")

    return sql


def read_sql(sql: str, db: str) -> pd.DataFrame:
    """
    Read data from SQL.

    Args:
        sql (str): SQL query to execute.
        db (str): Name of the database to connect to.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the results of the SQL query.
    """

    logger = get_dagster_logger()

    sql = db_translate(sql, db)

    logger.debug(f"sql:\n{sql}")

    if db == "bigquery":
        df = read_sql_bigquery(sql)
    elif db == "snowflake":
        df = read_sql_snowflake(sql)
    elif db == "duckdb":
        df = read_sql_duckdb(sql)
    else:
        raise ValueError(f"Unknown db: {db}")

    logger.debug(f"df:\n{df}")

    return df
