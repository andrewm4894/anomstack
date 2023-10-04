"""
Some utility functions.
"""

from dagster import get_dagster_logger
import pandas as pd
import os
import json
from google.oauth2 import service_account


def get_google_credentials():
    """
    Attempt to retrieve Google credentials from environment variables.

    First, try to get a file path from GOOGLE_APPLICATION_CREDENTIALS and load credentials from it.
    If that fails, try to load credentials from a JSON string in GOOGLE_APPLICATION_CREDENTIALS_JSON.

    Returns:
        google.auth.credentials.Credentials or None: Google credentials or None if credentials
        cannot be retrieved or parsed.
    """

    logger = get_dagster_logger()

    # Check for file path credentials
    credentials_path = os.getenv('ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS')
    credentials = None

    if credentials_path:
        try:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            logger.info(f"Loaded credentials from file path: {credentials_path}")
        except Exception as e:
            logger.info(f"Failed to load credentials from file with: {str(e)}. Trying to load from JSON string...")

    # If credentials could not be loaded from file path, try JSON string
    if credentials is None:
        raw_credentials = os.getenv('ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS_JSON')

        if raw_credentials:
            try:
                credentials_json = json.loads(raw_credentials)
                credentials = service_account.Credentials.from_service_account_info(credentials_json)
                logger.info("Loaded credentials from JSON string")
            except json.JSONDecodeError as e:
                logger.info(f"Failed to parse JSON credentials with: {str(e)}")

    return credentials


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
        gcp_project_id=gcp_project_id,
        if_exists=if_exists,
        credentials=credentials,
    )

    return df
