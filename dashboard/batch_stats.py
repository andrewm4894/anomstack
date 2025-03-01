from datetime import datetime
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
    avg_score = (
        df["metric_score"].fillna(0).mean() if "metric_score" in df.columns else 0
    )
    alert_count = (
        df["metric_alert"].fillna(0).sum() if "metric_alert" in df.columns else 0
    )

    # Calculate time ago string
    latest_timestamp = df["metric_timestamp"].max()
    time_ago_str = _format_time_ago(latest_timestamp)

    return {
        "unique_metrics": len(df["metric_name"].unique()),
        "latest_timestamp": time_ago_str,
        "avg_score": avg_score,
        "alert_count": alert_count,
    }


def _format_time_ago(timestamp: str) -> str:
    """Format a timestamp into a human readable time ago string."""
    if timestamp == "No data":
        return timestamp

    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    now = datetime.now(dt.tzinfo)
    diff_seconds = (now - dt).total_seconds()

    if diff_seconds < 3600:  # Less than 1 hour
        minutes_ago = round(diff_seconds / 60, 1)
        return f"{minutes_ago:.1f} minute{'s' if minutes_ago != 1 else ''} ago"
    elif diff_seconds < 86400:  # Less than 24 hours
        hours_ago = round(diff_seconds / 3600, 1)
        return f"{hours_ago:.1f} hour{'s' if hours_ago != 1 else ''} ago"
    else:  # Days or more
        days_ago = round(diff_seconds / 86400, 1)
        return f"{days_ago:.1f} day{'s' if days_ago != 1 else ''} ago"
