from io import StringIO

import pandas as pd
from dagster import get_dagster_logger


def log_df_info(df: pd.DataFrame, logger=None):
    """
    Logs the info of a DataFrame to the logger.

    Parameters:
    df (pd.DataFrame): The DataFrame whose info needs to be logged.
    """
    if not logger:
        logger = get_dagster_logger()
    buffer = StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    logger.info("df.info():\n%s", info_str)
