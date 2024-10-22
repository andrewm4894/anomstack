"""
This module provides functions for reading data from SQL databases using different database connectors.
"""

import re

import pandas as pd
import sqlglot
from dagster import get_dagster_logger

from anomstack.external.duckdb.duckdb import read_sql_duckdb
from anomstack.external.gcp.bigquery import read_sql_bigquery
from anomstack.external.snowflake.snowflake import read_sql_snowflake
from anomstack.external.sqlite.sqlite import read_sql_sqlite


def db_translate(sql: str, db: str) -> str:
    """
    Replace some functions with their db-specific equivalents.

    Args:
        sql (str): The SQL query to be translated.
        db (str): The name of the database to which the query will be sent.

    Returns:
        str: The translated SQL query.
    """
    # Transpile the SQL query to the target database dialect
    sql = sqlglot.transpile(sql, write=db, identify=True, pretty=True)[0]
    # Replace some functions with their db-specific equivalents
    if db == "sqlite":
        sql = sql.replace("GET_CURRENT_TIMESTAMP()", "DATETIME('now')")
    elif db == "bigquery":
        sql = sql.replace("GET_CURRENT_TIMESTAMP()", "CURRENT_TIMESTAMP()")
        sql = re.sub(r"DATE\('now', '(-?\d+) day'\)", "DATE_ADD(CURRENT_DATE(), INTERVAL \\1 DAY)", sql)

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
    elif db == "sqlite":
        df = read_sql_sqlite(sql)
    else:
        raise ValueError(f"Unknown db: {db}")

    logger.debug(f"df:\n{df}")

    return df
