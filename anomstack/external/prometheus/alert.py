"""
Prometheus query processing for alert jobs.

Handles getting anomaly scores for alert evaluation.
"""

import pandas as pd
from dagster import get_dagster_logger
from typing import Dict
from anomstack.external.prometheus.prometheus import read_sql_prometheus


def execute_prometheus_alert_query(spec: Dict) -> pd.DataFrame:
    """
    Execute Prometheus query equivalent to alerts.sql.
    
    Gets anomaly scores for alert evaluation.
    
    Args:
        spec: Metric batch specification
        
    Returns:
        pd.DataFrame: Alert data in expected format
    """
    logger = get_dagster_logger()
    logger.info("Executing Prometheus alert query")
    
    metric_batch = spec.get("metric_batch", "")
    alert_metric_timestamp_max_days_ago = spec.get("alert_metric_timestamp_max_days_ago", 1)
    
    # Get anomaly scores for alerting
    promql = "{__name__=~'.*_anomaly_score'}"
    
    df = read_sql_prometheus(
        promql,
        query_type="query_range",
        start=f"now-{alert_metric_timestamp_max_days_ago}d",
        end="now",
        step="300s"
    )
    
    if not df.empty:
        df["metric_batch"] = metric_batch
        df["metric_type"] = "score"
        
        # Remove the _anomaly_score suffix from metric names to match expected format
        df["metric_name"] = df["metric_name"].str.replace("_anomaly_score", "", regex=False)
        
        logger.info(f"Retrieved {len(df)} anomaly scores for alerting")
    
    return df 