"""
Prometheus query processing for LLM alert jobs.

Handles getting anomaly scores for LLM-based alerting.
"""

import pandas as pd
from dagster import get_dagster_logger
from typing import Dict
from anomstack.external.prometheus.prometheus import read_sql_prometheus


def execute_prometheus_llmalert_query(spec: Dict) -> pd.DataFrame:
    """
    Execute Prometheus query equivalent to llmalert.sql.
    
    Gets anomaly scores for LLM-based alert evaluation.
    
    Args:
        spec: Metric batch specification
        
    Returns:
        pd.DataFrame: LLM alert data
    """
    logger = get_dagster_logger()
    logger.info("Executing Prometheus LLM alert query")
    
    metric_batch = spec.get("metric_batch", "")
    llmalert_metric_timestamp_max_days_ago = spec.get("llmalert_metric_timestamp_max_days_ago", 1)
    
    # Get anomaly scores for LLM alerting
    promql = "{__name__=~'.*_anomaly_score'}"
    
    df = read_sql_prometheus(
        promql,
        query_type="query_range",
        start=f"now-{llmalert_metric_timestamp_max_days_ago}d",
        end="now", 
        step="300s"
    )
    
    if not df.empty:
        df["metric_batch"] = metric_batch
        df["metric_type"] = "score"
        df["metric_name"] = df["metric_name"].str.replace("_anomaly_score", "", regex=False)
        logger.info(f"Retrieved {len(df)} anomaly scores for LLM alerting")
    
    return df 