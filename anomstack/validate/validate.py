"""
Some helper functions to validate dataframes.
"""

from io import StringIO

import pandas as pd
from dagster import get_dagster_logger


def validate_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the dataframe.

    Args:
        df (pd.DataFrame): The dataframe to be validated.

    Returns:
        pd.DataFrame: The validated dataframe.
    """

    logger = get_dagster_logger()

    buffer = StringIO()
    df.info(buf=buffer, verbose=True)
    info_str = buffer.getvalue()
    logger.debug(f"df.info(): \n{info_str}")

    # validate the dataframe
    assert "metric_type" in df.columns.str.lower(), "metric_type column missing"
    assert "metric_batch" in df.columns.str.lower(), "metric_batch column missing"
    assert "metric_name" in df.columns.str.lower(), "metric_name column missing"
    assert "metric_value" in df.columns.str.lower(), "metric_value column missing"
    assert "metadata" in df.columns.str.lower(), "metadata column missing"
    assert (
        "metric_timestamp" in df.columns.str.lower()
    ), "metric_timestamp column missing"
    assert len(df.columns) == 6, f"expected 6 columns, got {len(df.columns)}"
    assert len(df) > 0, "no data returned"

    # metric_name is string
    assert df["metric_name"].dtype == "object", "metric_name is not string"
    # metric_value is numeric
    assert pd.api.types.is_numeric_dtype(
        df["metric_value"]
    ), "metric_value is not numeric"
    # metric_timestamp is timestamp
    assert pd.api.types.is_datetime64_any_dtype(
        df["metric_timestamp"]
    ), "metric_timestamp is not timestamp"

    return df
