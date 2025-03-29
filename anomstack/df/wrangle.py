"""
Some helper functions for wrangling data.
"""

import pandas as pd
from dagster import get_dagster_logger
import numpy as np
import json


def wrangle_df(df: pd.DataFrame, rounding: int = 4) -> pd.DataFrame:
    """
    Wrangle the given DataFrame to ensure its structure and data quality.

    Args:
        df (pd.DataFrame): The DataFrame to be wrangled.
        rounding (int, optional): The number of decimal places to round the
            'metric_value' column to. Defaults to 4.

    Returns:
        pd.DataFrame: The wrangled DataFrame.

    """
    logger = get_dagster_logger()

    # ensure metric_value is numeric
    df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")

    # ensure metric_timestamp is timestamp
    df["metric_timestamp"] = pd.to_datetime(df["metric_timestamp"], errors="coerce")

    # if metadata is not in df then add as empty string
    if "metadata" not in df.columns:
        df["metadata"] = ""

    # enforce column order
    df = df[
        [
            "metric_timestamp",
            "metric_batch",
            "metric_name",
            "metric_type",
            "metric_value",
            "metadata",
        ]
    ]

    # if we have any nan metric_values then drop them and log how many
    # nan rows we dropped
    if df["metric_value"].isnull().sum() > 0:
        logger.warning(
            f"dropping {df['metric_value'].isnull().sum()} nan " "metric_value rows"
        )
        df = df[~df["metric_value"].isnull()]

    # round metric_value
    df["metric_value"] = df["metric_value"].round(rounding)

    return df


def extract_metadata(df: pd.DataFrame, key_name: str) -> pd.DataFrame:
    """Extract a key from the metadata column."""
    if "metadata" not in df.columns:
        return df
    
    def safe_extract(x):
        try:
            # First handle the case where x is a list/array
            if isinstance(x, (list, np.ndarray)):
                # Get the first non-None element
                filtered = [item for item in x if item is not None]
                if not filtered:
                    return None
                x = filtered[0]
            
            # Now handle the single value
            if pd.isna(x) or x is None or x == '':
                return None
            
            # Skip empty strings or whitespace
            if not isinstance(x, str) or not x.strip():
                return None
            
            parsed = json.loads(x)
            return parsed.get(key_name)
            
        except (json.JSONDecodeError, AttributeError, IndexError, TypeError) as e:
            return None

    df = df.copy()
    df[key_name] = df["metadata"].apply(safe_extract)
    
    # Convert any 'None' strings to None
    df[key_name] = df[key_name].apply(lambda x: None if x == 'None' else x)
    
    return df
