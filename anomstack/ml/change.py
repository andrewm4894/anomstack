"""
Module for detecting change in a metric based on the Median Absolute Deviation
(MAD) method.
"""

import numpy as np
import pandas as pd
from pyod.models.mad import MAD

from dagster import get_dagster_logger


def detect_change(
    df_metric: pd.DataFrame, threshold: float = 3.5, detect_last_n: int = 1
) -> pd.DataFrame:
    """
    Detects change in a metric based on the Median Absolute Deviation (MAD)
        method.

    Args:
        df_metric (pd.DataFrame): DataFrame containing the metric data.
        threshold (float, optional): Threshold value for detecting change.
            Defaults to 3.5.
        detect_last_n (int, optional): Number of last observations to use for
            detection. Defaults to 1.

    Returns:
        pd.DataFrame: DataFrame with the detected change information.
    """
    # TODO: clean this all up a little once happy with the logic
    logger = get_dagster_logger()
    metric_name = df_metric["metric_name"].unique()[0]
    logger.debug(f"beginning change detection for {metric_name}")
    detector = MAD(threshold=threshold)
    X_train = df_metric["metric_value"].values[:-detect_last_n].reshape(-1, 1)
    X_detect = df_metric["metric_value"].values[-detect_last_n:].reshape(-1, 1)
    X_detect_timestamps = df_metric["metric_timestamp"].values[-detect_last_n:]
    detector.fit(X_train)
    X_train_scores = detector.decision_scores_
    y_detect_scores = detector.decision_function(X_detect)
    logger.debug(f"y_detect_scores: {y_detect_scores}")
    df_metric["metric_score"] = list(X_train_scores) + list(y_detect_scores)
    df_metric["metric_alert"] = np.where(
        (df_metric["metric_score"] > threshold)
        & (df_metric["metric_timestamp"].isin(X_detect_timestamps)),
        1,
        0,
    )
    logger.debug(f"df_metric:\n{df_metric}")
    if df_metric["metric_alert"].sum() > 0:
        logger.info(f"change detected for {metric_name} at {X_detect_timestamps}")

        return df_metric
    else:
        logger.info(f"no change detected for {metric_name} at {X_detect_timestamps}")

        return pd.DataFrame()
