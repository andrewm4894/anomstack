"""
This module provides functions for reading data from SQL databases using
different database connectors.
"""


import pandas as pd
from dagster import get_dagster_logger

from anomstack.df.utils import log_df_info
from anomstack.external.clickhouse.clickhouse import (
    read_sql_clickhouse,
    run_sql_clickhouse,
)
from anomstack.external.duckdb.duckdb import read_sql_duckdb, run_sql_duckdb
from anomstack.external.gcp.bigquery import read_sql_bigquery
from anomstack.external.snowflake.snowflake import read_sql_snowflake
from anomstack.external.sqlite.sqlite import read_sql_sqlite, run_sql_sqlite
from anomstack.sql.translate import db_translate

pd.options.display.max_columns = 10


def read_sql(sql: str, db: str, returns_df: bool = True) -> pd.DataFrame:
    """
    Read data from SQL.

    Args:
        sql (str): SQL query to execute.
        db (str): Name of the database to connect to.
        returns_df (bool, optional): Whether the query expects a DataFrame as a result.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the results of the SQL query.
    """

    logger = get_dagster_logger()

    sql = db_translate(sql, db)

    logger.debug(f"-- read_sql() is about to read this qry:\n{sql}")

    if db == "bigquery":
        if returns_df:
            df = read_sql_bigquery(sql)
        elif not returns_df:
            raise NotImplementedError(
                "BigQuery not yet implemented for non-returns_df queries."
            )
    elif db == "snowflake":
        if returns_df:
            df = read_sql_snowflake(sql)
        elif not returns_df:
            raise NotImplementedError(
                "Snowflake not yet implemented for non-returns_df queries."
            )
    elif db == "duckdb":
        if returns_df:
            df = read_sql_duckdb(sql)
        elif not returns_df:
            run_sql_duckdb(sql)
            df = pd.DataFrame()
    elif db == "sqlite":
        if returns_df:
            df = read_sql_sqlite(sql)
        elif not returns_df:
            run_sql_sqlite(sql)
            df = pd.DataFrame()
    elif db == "clickhouse":
        if returns_df:
            df = read_sql_clickhouse(sql)
        elif not returns_df:
            run_sql_clickhouse(sql)
            df = pd.DataFrame()
    else:
        raise ValueError(f"Unknown db: {db}")

    log_df_info(df, logger)
    logger.debug(f"df.head():\n{df.head()}")
    logger.debug(f"df.tail():\n{df.tail()}")

    return df
