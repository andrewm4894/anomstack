"""
"""

from dagster import get_dagster_logger
import pandas as pd
from anomstack.gcp.credentials import get_google_credentials


def read_sql_bigquery(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """

    logger = get_dagster_logger()

    logger.info(f'sql:\n{sql}')

    credentials = get_google_credentials()

    df = pd.read_gbq(
        query=sql,
        credentials=credentials,
    )
    logger.info(f'df:\n{df}')

    return df


def save_df_bigquery(df, table_key, gcp_project_id, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """

    credentials = get_google_credentials()

    df.to_gbq(
        destination_table=table_key,
        project_id=gcp_project_id,
        if_exists=if_exists,
        credentials=credentials,
    )

    return df
