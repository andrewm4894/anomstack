import pandas as pd
from dagster import get_dagster_logger


def wrangle_df(df: pd.DataFrame, rounding: int = 4) -> pd.DataFrame:
    """
    Wrangle the df to ensure its as expected.
    """

    logger = get_dagster_logger()

    # ensure metric_value is numeric
    df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")

    # ensure metric_timestamp is timestamp
    df["metric_timestamp"] = pd.to_datetime(df["metric_timestamp"], errors="coerce")

    # enforce column order
    df = df[
        [
            "metric_timestamp",
            "metric_batch",
            "metric_name",
            "metric_type",
            "metric_value",
        ]
    ]

    # if we have any nan metric_values then drop them and log how many nan rows we dropped
    if df["metric_value"].isnull().sum() > 0:
        logger.warning(f"dropping {df['metric_value'].isnull().sum()} nan metric_value rows")
        df = df[~df["metric_value"].isnull()]

    # round metric_value
    df["metric_value"] = df["metric_value"].round(rounding)

    return df
