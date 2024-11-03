"""
Module for detecting change in a metric based on the Median Absolute Deviation
(MAD) method.
"""

import numpy as np
import pandas as pd
from dagster import get_dagster_logger
from pyod.models.mad import MAD

from anomstack.df.utils import log_df_info

pd.options.display.max_columns = 10


def detect_change(
    df_metric: pd.DataFrame,
    threshold: float = 3.5,
    detect_last_n: int = 1
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
    df_metric["metric_change_calculated"] = np.where(
        df_metric["metric_score"] > threshold, 1, 0
    )
    df_metric["metric_alert"] = df_metric["metric_change"].combine_first(
        df_metric["metric_change_calculated"]
    )
    log_df_info(df_metric, logger)
    logger.debug(f"df_metric.head(10):\n{df_metric.head(10)}")
    logger.debug(f"df_metric.tail(10):\n{df_metric.tail(10)}")
    change_detected_count = df_metric["metric_alert"].tail(detect_last_n).sum()
    if change_detected_count > 0:
        logger.info(
            f"change detected for {metric_name} at {X_detect_timestamps}"
        )
        return df_metric
    else:
        logger.info(
            f"no change detected for {metric_name} at {X_detect_timestamps}"
        )

        return pd.DataFrame()
