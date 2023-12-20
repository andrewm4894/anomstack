"""
This module provides functions to save Pandas DataFrames to various databases.

Functions:
- save_df: Save a Pandas DataFrame to a database.
"""

import pandas as pd

from anomstack.external.duckdb.duckdb import save_df_duckdb
from anomstack.external.gcp.bigquery import save_df_bigquery
from anomstack.external.snowflake.snowflake import save_df_snowflake


def save_df(df, db, table_key, if_exists="append") -> pd.DataFrame:
    """
    Save a Pandas DataFrame to a database.

    Args:
    - df: The Pandas DataFrame to save.
    - db: The name of the database to save to. Must be one of 'bigquery', 'snowflake', or 'duckdb'.
    - table_key: A string identifying the table to save to.
    - if_exists: What to do if the table already exists. Must be one of 'fail', 'replace', or 'append'. Default is 'append'.

    Returns:
    - The Pandas DataFrame that was saved.
    """
    if db == "bigquery":
        df = save_df_bigquery(df, table_key, if_exists)
    elif db == "snowflake":
        df = save_df_snowflake(df, table_key)
    elif db == "duckdb":
        df = save_df_duckdb(df, table_key)
    else:
        raise ValueError(f"Unknown db: {db}")

    return df
