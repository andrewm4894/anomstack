"""
dashboard/batch_stats.py

Batch Stats

This module contains functions for calculating statistics for a batch of metrics.

"""

from datetime import datetime, timezone
import pandas as pd
from typing import Dict, Any


def calculate_batch_stats(df: pd.DataFrame, batch_name: str) -> Dict[str, Any]:
    """Calculate statistics for a batch of metrics."""
    if df.empty:
        return {
            "unique_metrics": 0,
            "latest_timestamp": "No data",
            "avg_score": 0,
            "alert_count": 0,
        }

    # Calculate core stats
    avg_score = (df["metric_score"].fillna(0).mean()
                 if "metric_score" in df.columns else 0)
    alert_count = (df["metric_alert"].fillna(0).sum()
                   if "metric_alert" in df.columns else 0)

    # Calculate time ago string
    latest_timestamp = df["metric_timestamp"].max()
    time_ago_str = _format_time_ago(latest_timestamp)

    return {
        "unique_metrics": len(df["metric_name"].unique()),
        "latest_timestamp": time_ago_str,
        "avg_score": avg_score,
        "alert_count": alert_count,
    }


def _format_time_ago(timestamp):
    """Format a timestamp into a human readable time ago string."""

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
