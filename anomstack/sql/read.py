"""
"""

from dagster import get_dagster_logger
import pandas as pd
from anomstack.external.gcp.bigquery import read_sql_bigquery
from anomstack.external.duckdb.duckdb import read_sql_duckdb
from anomstack.external.snowflake.snowflake import read_sql_snowflake


def db_translate(sql, db) -> str:
    """
    Function that will replace some functions with their db-specific equivalents.
    """
    if db == "bigquery":
        sql = sql.replace("now()", "current_timestamp()")

    return sql


def read_sql(sql, db) -> pd.DataFrame:
    """
    Read data from SQL.
    """

    logger = get_dagster_logger()

    sql = db_translate(sql, db)

    logger.info(f"sql:\n{sql}")
    if db == "bigquery":
        df = read_sql_bigquery(sql)
    elif db == "snowflake":
        df = read_sql_snowflake(sql)
    elif db == "duckdb":
        df = read_sql_duckdb(sql)
    else:
        raise ValueError(f"Unknown db: {db}")
    logger.info(f"df:\n{df}")

    return df
