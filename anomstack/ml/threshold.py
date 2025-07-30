"""
Threshold-based anomaly detection.
"""

from dagster import get_dagster_logger
import pandas as pd


def detect_threshold_alerts(
    df: pd.DataFrame, thresholds: dict, recent_n: int = 1, snooze_n: int = 3
) -> pd.DataFrame:
    """
    Detect threshold-based alerts.

    Args:
        df (pd.DataFrame): DataFrame with columns ['metric_timestamp', 'metric_name', 'metric_value']
        thresholds (dict): Dictionary mapping metric names to threshold definitions
                          e.g., {'cpu_usage': {'upper': 90, 'lower': 10}}
        recent_n (int): Only consider the most recent n observations for alerting
        snooze_n (int): Number of periods to snooze after an alert

    Returns:
        pd.DataFrame: DataFrame with additional columns ['threshold_alert', 'threshold_type', 'threshold_value']
    """
    logger = get_dagster_logger()

    if df.empty:
        logger.info("No data to process for threshold alerts")
        return df

    # Add threshold alert columns
    df = df.copy()
    df["threshold_alert"] = 0
    df["threshold_type"] = None  # 'upper' or 'lower'
    df["threshold_value"] = None  # the threshold value that was breached

    if not thresholds:
        logger.info("No thresholds configured")
        return df

    for metric_name in df["metric_name"].unique():
        if metric_name not in thresholds:
            continue

        metric_thresholds = thresholds[metric_name]
        df_metric = df[df["metric_name"] == metric_name].copy()

        if df_metric.empty:
            continue

        # Sort by timestamp to get most recent observations
        df_metric = df_metric.sort_values("metric_timestamp").reset_index(drop=True)

        # Only check recent observations for alerting
        recent_observations = df_metric.tail(recent_n)

        # Track alerts we've already set in this processing loop
        alerts_set_positions = []

        for idx, row in recent_observations.iterrows():
            metric_value = row["metric_value"]

            # Find the original index in the full dataframe
            mask = (df["metric_name"] == metric_name) & (
                df["metric_timestamp"] == row["metric_timestamp"]
            )
            matching_rows = df[mask]
            if matching_rows.empty:
                continue
            original_idx = matching_rows.index[0]

            # Find current position in df_metric (use the reset index position)
            current_pos = (
                df_metric.reset_index(drop=True)
                .index[df_metric["metric_timestamp"] == row["metric_timestamp"]]
                .tolist()[0]
            )

            # Check if we should snooze (look back snooze_n periods for recent alerts)
            lookback_start = max(0, current_pos - snooze_n)

            # Check for recent alerts both in already processed data and alerts set in this loop
            recent_alert_positions = [
                pos for pos in alerts_set_positions if pos >= lookback_start and pos < current_pos
            ]
            if recent_alert_positions:
                continue  # Skip due to snoozing

            # Check thresholds
            alert_triggered = False
            if "upper" in metric_thresholds and metric_value > metric_thresholds["upper"]:
                df.loc[original_idx, "threshold_alert"] = 1
                df.loc[original_idx, "threshold_type"] = "upper"
                df.loc[original_idx, "threshold_value"] = metric_thresholds["upper"]
                logger.info(
                    f"Upper threshold alert for {metric_name}: {metric_value} > {metric_thresholds['upper']}"
                )
                alert_triggered = True

            elif "lower" in metric_thresholds and metric_value < metric_thresholds["lower"]:
                df.loc[original_idx, "threshold_alert"] = 1
                df.loc[original_idx, "threshold_type"] = "lower"
                df.loc[original_idx, "threshold_value"] = metric_thresholds["lower"]
                logger.info(
                    f"Lower threshold alert for {metric_name}: {metric_value} < {metric_thresholds['lower']}"
                )
                alert_triggered = True

            if alert_triggered:
                alerts_set_positions.append(current_pos)

    # Count final alerts
    threshold_alerts = df[df["threshold_alert"] == 1]
    if len(threshold_alerts) > 0:
        logger.info(f"Generated {len(threshold_alerts)} threshold alerts")
    else:
        logger.info("No threshold alerts generated")

    return df
