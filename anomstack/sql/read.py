"""
"""

from dagster import get_dagster_logger
import pandas as pd
from anomstack.utils.bigquery import read_sql_bigquery
from anomstack.utils.duckdb import read_sql_duckdb


def read_sql(sql, db) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    
    logger.debug(f'sql:\n{sql}')
    if db=='bigquery':
        df = read_sql_bigquery(sql)
    elif db=='duckdb':
        df = read_sql_duckdb(sql)
    else:
        raise ValueError(f'Unknown db: {db}')
    logger.debug(f'df:\n{df}')
    
    return df
