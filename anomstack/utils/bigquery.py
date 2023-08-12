"""
Some utility functions.
"""

from dagster import get_dagster_logger
import pandas as pd


def read_sql_bigquery(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    
    logger.debug(f'sql:\n{sql}')
    df = pd.read_gbq(query=sql)
    logger.debug(f'df:\n{df}')
    
    return df


def save_df_bigquery(df, table_key, gcp_project_id, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """

    df.to_gbq(
        destination_table=table_key,
        gcp_project_id=gcp_project_id,
        if_exists=if_exists,
    )
    
    return df

