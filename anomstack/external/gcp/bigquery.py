"""
"""

import os
import random
import time

import pandas as pd
from dagster import get_dagster_logger
from google.api_core.exceptions import Forbidden
from google.cloud import bigquery
from google.cloud.exceptions import TooManyRequests

from anomstack.external.gcp.credentials import get_google_credentials


def read_sql_bigquery(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """

    logger = get_dagster_logger()

    logger.debug(f"sql:\n{sql}")

    credentials = get_google_credentials()

    df = pd.read_gbq(
        query=sql,
        credentials=credentials,
    )
    logger.debug(f"df:\n{df}")

    return df


def pandas_save_df_bigquery(df, table_key, if_exists="append") -> pd.DataFrame:
    """
    Save df to db.
    """

    table_key_parts = table_key.split(".")

    if len(table_key_parts) == 2:
        project_id = os.getenv("ANOMSTACK_GCP_PROJECT_ID")
        assert (
            project_id is not None
        ), f"ANOMSTACK_GCP_PROJECT_ID must be set in environment if table_key is not fully qualified: {table_key}"
        table_key_parts = [project_id] + table_key_parts

    assert (
        len(table_key_parts) == 3
    ), f"Invalid table_key: {table_key}, should be <project_id>.<dataset_id>.<table_id>"

    project_id = table_key_parts[0]
    dataset_id = table_key_parts[1]
    table_id = table_key_parts[2]

    credentials = get_google_credentials()

    df.to_gbq(
        destination_table=f"{dataset_id}.{table_id}",
        project_id=project_id,
        if_exists=if_exists,
        credentials=credentials,
    )

    return df


def save_df_bigquery(df, table_key, if_exists="append", max_retries=5) -> pd.DataFrame:
    """
    Save df to db, with exponential backoff retry for handling rate limit exceeded error.
    """
    table_key_parts = table_key.split(".")
    if len(table_key_parts) == 2:
        project_id = os.getenv("ANOMSTACK_GCP_PROJECT_ID")
        assert (
            project_id is not None
        ), "ANOMSTACK_GCP_PROJECT_ID must be set in environment if table_key is not fully qualified."
        table_key_parts = [project_id] + table_key_parts

    assert (
        len(table_key_parts) == 3
    ), "Invalid table_key, should be <project_id>.<dataset_id>.<table_id>"

    project_id, dataset_id, table_id = table_key_parts

    credentials = get_google_credentials()

    client = bigquery.Client(credentials=credentials, project=project_id)

    destination_table = f"{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.job.WriteDisposition.WRITE_APPEND
        if if_exists == "append"
        else bigquery.job.WriteDisposition.WRITE_TRUNCATE
    )

    for attempt in range(max_retries):
        try:
            job = client.load_table_from_dataframe(
                dataframe=df, destination=destination_table, job_config=job_config
            )
            job.result()  # Wait for the job to complete
            break  # Success, exit the retry loop
        except (TooManyRequests, Forbidden) as e:
            wait_time = 2**attempt + random.uniform(
                0, 1
            )  # Exponential backoff with jitter
            get_dagster_logger().warning(
                f"Exceeded rate limits on attempt {attempt+1}. Retrying in {wait_time} seconds."
            )
            time.sleep(wait_time)
    else:
        raise RuntimeError(
            f"Failed to save data to BigQuery after {max_retries} attempts."
        )

    return df
