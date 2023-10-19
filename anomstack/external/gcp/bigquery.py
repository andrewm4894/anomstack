"""
"""

from dagster import get_dagster_logger
import pandas as pd
from anomstack.external.gcp.credentials import get_google_credentials
import os


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


def save_df_bigquery(df, table_key, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """

    table_key_parts = table_key.split('.')

    if len(table_key_parts) == 2:
        project_id = os.getenv('ANOMSTACK_GCP_PROJECT_ID')
        assert project_id is not None, f'ANOMSTACK_GCP_PROJECT_ID must be set in environment if table_key is not fully qualified: {table_key}'
        table_key_parts = [project_id] + table_key_parts

    assert len(table_key_parts) == 3, f'Invalid table_key: {table_key}, should be <project_id>.<dataset_id>.<table_id>'

    project_id = table_key_parts[0]
    dataset_id = table_key_parts[1]
    table_id = table_key_parts[2]

    credentials = get_google_credentials()

    df.to_gbq(
        destination_table=f'{dataset_id}.{table_id}',
        project_id=project_id,
        if_exists=if_exists,
        credentials=credentials,
    )

    return df
