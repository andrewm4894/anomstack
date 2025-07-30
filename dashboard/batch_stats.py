"""
dashboard/batch_stats.py

Batch Stats

This module contains functions for calculating statistics for a batch of metrics.

"""

from datetime import datetime, timezone
from typing import Any, Dict

import pandas as pd


def calculate_batch_stats(df: pd.DataFrame, batch_name: str) -> Dict[str, Any]:
    """Calculate statistics for a batch of metrics.

    Args:
        df (pd.DataFrame): The dataframe containing the metrics.
        batch_name (str): The name of the batch to calculate stats for.

    Returns:
        Dict[str, Any]: A dictionary containing the statistics.
    """
    if df.empty:
        return {
            "unique_metrics": 0,
            "latest_timestamp": "No data",
            "avg_score": 0,
            "alert_count": 0,
        }

    # Calculate core stats
    avg_score = df["metric_score"].fillna(0).mean() if "metric_score" in df.columns else 0
    alert_count = df["metric_alert"].fillna(0).sum() if "metric_alert" in df.columns else 0
    llmalert_count = df["metric_llmalert"].fillna(0).sum() if "metric_llmalert" in df.columns else 0
    change_count = df["metric_change"].fillna(0).sum() if "metric_change" in df.columns else 0
    alert_count = alert_count + llmalert_count + change_count

    # Calculate time ago string
    latest_timestamp = df["metric_timestamp"].max()
    time_ago_str = format_time_ago(latest_timestamp)

    return {
        "unique_metrics": len(df["metric_name"].unique()),
        "latest_timestamp": time_ago_str,
        "avg_score": avg_score,
        "alert_count": alert_count,
    }


def format_time_ago(timestamp: str) -> str:
    """Format a timestamp into a human readable time ago string.

    Args:
        timestamp (str): The timestamp to format.

    Returns:
        str: The formatted time ago string.
    """
    timestamp = str(timestamp)
    timestamp = timestamp.replace("Z", "+00:00")

    dt = datetime.fromisoformat(timestamp)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - dt

    if delta.days > 0:
        return f"{delta.days} days ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600} hours ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60} minutes ago"
    else:
        return "just now"
