"""
Some utility functions.
"""

from dagster import get_dagster_logger
import pandas as pd
import jinja2
from jinja2 import FileSystemLoader
import requests
import json
import os
import duckdb


def read_sql_duckdb(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    
    duckdb_path = os.environ.get('ANOMSTACK_DUCKDB_PATH','./tmp/anomstack.db')
    
    conn = duckdb.connect(duckdb_path)
    
    logger.info(f'sql:\n{sql}')
    df = duckdb.query(connection=conn, query=sql).df()
    logger.info(f'df:\n{df}')
    
    return df


def save_df_duckdb(df, table_key) -> pd.DataFrame:
    """
    Save df to db.
    """
    
    duckdb_path = os.environ.get('ANOMSTACK_DUCKDB_PATH','./tmp/anomstack.db')
    conn = duckdb.connect(duckdb_path)

    try:
        if '.' in table_key:
            schema, _ = table_key.split('.')
            duckdb.query(connection=conn, query=f'CREATE SCHEMA IF NOT EXISTS {schema}')
        duckdb.query(connection=conn, query=f'INSERT INTO {table_key} SELECT * FROM df')
    except:
        duckdb.query(connection=conn, query=f'CREATE TABLE {table_key} AS SELECT * FROM df')
    
    return df
