"""
Prometheus query processing for score jobs.

Handles getting raw metrics for anomaly scoring.
"""

import pandas as pd
from dagster import get_dagster_logger
from typing import Dict
from anomstack.external.prometheus.prometheus import read_sql_prometheus


def execute_prometheus_score_query(spec: Dict) -> pd.DataFrame:
    """
    Execute Prometheus query equivalent to score.sql.
    
    Gets raw metrics for scoring (recent data that needs anomaly scores).
    
    Args:
        spec: Metric batch specification
        
    Returns:
        pd.DataFrame: Scoring data in expected format
    """
    logger = get_dagster_logger()
    logger.info("Executing Prometheus score query")
    
    metric_batch = spec.get("metric_batch", "")
    score_metric_timestamp_max_days_ago = spec.get("score_metric_timestamp_max_days_ago", 1)
    
    # Get raw metrics for scoring
    promql = "{__name__!~'.*_(anomaly_score|alert|llm_alert|threshold_alert)'}"
    
    df = read_sql_prometheus(
        promql,
        query_type="query_range", 
        start=f"now-{score_metric_timestamp_max_days_ago}d",
        end="now",
        step="300s"
    )
    
    if not df.empty:
        df["metric_batch"] = metric_batch
        df["metric_type"] = "metric"
        
        # For score job, we typically want recent data that doesn't have scores yet
        # This is simplified - in practice you'd check for missing scores
        logger.info(f"Retrieved {len(df)} rows for scoring")
    
    return df 