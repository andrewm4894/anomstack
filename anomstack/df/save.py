"""
"""

import pandas as pd
from anomstack.gcp.bigquery import save_df_bigquery
from anomstack.utils.duckdb import save_df_duckdb


def save_df(df, db, table_key, gcp_project_id, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """

    if db=='bigquery':
        df = save_df_bigquery(df, table_key, gcp_project_id, if_exists)
    elif db=='duckdb':
        df = save_df_duckdb(df, table_key)
    else:
        raise ValueError(f'Unknown db: {db}')
    
    return df
