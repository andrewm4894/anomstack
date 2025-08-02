"""
Prometheus query processing for change detection jobs.

Handles getting raw metrics for change point detection.
"""

import pandas as pd
from dagster import get_dagster_logger
from typing import Dict
from anomstack.external.prometheus.prometheus import read_sql_prometheus


def execute_prometheus_change_query(spec: Dict) -> pd.DataFrame:
    """
    Execute Prometheus query equivalent to change.sql.
    
    Gets raw metrics for change point detection.
    
    Args:
        spec: Metric batch specification
        
    Returns:
        pd.DataFrame: Change detection data
    """
    logger = get_dagster_logger()
    logger.info("Executing Prometheus change query")
    
    metric_batch = spec.get("metric_batch", "")
    change_metric_timestamp_max_days_ago = spec.get("change_metric_timestamp_max_days_ago", 7)
    
    promql = "{__name__!~'.*_(anomaly_score|alert|llm_alert|threshold_alert)'}"
    
    df = read_sql_prometheus(
        promql,
        query_type="query_range",
        start=f"now-{change_metric_timestamp_max_days_ago}d", 
        end="now",
        step="300s"
    )
    
    if not df.empty:
        df["metric_batch"] = metric_batch
        df["metric_type"] = "metric"
        logger.info(f"Retrieved {len(df)} rows for change detection")
    
    return df 