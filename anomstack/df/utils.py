from io import StringIO
from dagster import get_dagster_logger
import pandas as pd


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
