"""
Some functions for preprocessing data for model training and scoring.
"""

import pandas as pd

from dagster import get_dagster_logger


def make_x(
    df: pd.DataFrame,
    mode: str = "train",
    diff_n: int = 0,
    smooth_n: int = 0,
    lags_n: int = 0,
    score_n: int = 1,
) -> pd.DataFrame:
    """
    Prepare data for model training and scoring.

    Parameters:
        df (pd.DataFrame): The input dataframe.
        mode (str): The mode of operation "train" or "score". Default is "train".
        diff_n (int): The order of differencing. Default is 0.
        smooth_n (int): The window size for smoothing (moving average). Default is 0.
        lags_n (int): The number of lags to include. Default is 0.
        score_n (int): The number of rows to include in score mode. Default is 1.

    Returns:
        pd.DataFrame: The preprocessed dataframe.

    Raises:
        ValueError: If mode is not "train" or "score".
    """

    logger = get_dagster_logger()

    X = (
        df.sort_values(by=["metric_timestamp"])
        .reset_index(drop=True)
        .set_index("metric_timestamp")
    )
    X = df[["metric_value"]]

    if diff_n > 0:
        X["metric_value"] = X["metric_value"].diff(periods=diff_n).dropna()

    if smooth_n > 0:
        X["metric_value"] = X["metric_value"].rolling(window=smooth_n).mean().dropna()

    if lags_n > 0:
        for lag in range(1, lags_n + 1):
            X[f"lag_{lag}"] = X["metric_value"].shift(lag)

    if mode == "train":
        X = X.sample(frac=1)

    elif mode == "score":
        X = X.tail(score_n)

    else:
        raise ValueError("mode must be 'train' or 'score'")

    X = X.dropna()

    logger.debug(f"X=\n{X}")

    return X
