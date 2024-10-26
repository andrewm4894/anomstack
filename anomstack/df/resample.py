"""
Some helper functions for resampling data.
"""

import pandas as pd

from dagster import get_dagster_logger


def resample(df: pd.DataFrame, freq: str, freq_agg: str = "mean") -> pd.DataFrame:
    """
    Resample df to a desired frequency.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        freq (str): The desired frequency for resampling.
        freq_agg (str): The aggregation method for resampling.

    Returns:
        pandas.DataFrame: The resampled DataFrame.

    Raises:
        ValueError: If an unsupported aggregation method is provided.

    """
    logger = get_dagster_logger()

    df = df.set_index("metric_timestamp")
    if freq_agg == "mean":
        df = df.groupby(["metric_batch", "metric_name"]).resample(freq).mean()
    elif freq_agg == "sum":
        df = df.groupby(["metric_batch", "metric_name"]).resample(freq).sum()
    else:
        raise ValueError(f"Unsupported aggregation method: {freq_agg}")
    df = df.reset_index()

    logger.debug(f"resampled data ({freq},{freq_agg}):\n{df.head()}")

    return df
