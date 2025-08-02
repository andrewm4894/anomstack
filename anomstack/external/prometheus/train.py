"""
Prometheus query processing for train jobs.

Handles getting raw metrics for model training with SQL-equivalent operations
like filtering, grouping, ranking, and row limiting.
"""

import pandas as pd
from dagster import get_dagster_logger
from typing import Dict
from anomstack.external.prometheus.prometheus import read_sql_prometheus


def execute_prometheus_train_query(spec: Dict) -> pd.DataFrame:
    """
    Execute Prometheus query equivalent to train.sql.
    
    Handles: time filtering, metric filtering, grouping, ranking, row limiting
    
    Args:
        spec: Metric batch specification with all config parameters
        
    Returns:
        pd.DataFrame: Training data in expected format
    """
    logger = get_dagster_logger()
    logger.info("Executing Prometheus train query")
    
    # Extract parameters from spec
    metric_batch = spec.get("metric_batch", "")
    train_metric_timestamp_max_days_ago = spec.get("train_metric_timestamp_max_days_ago", 7)
    train_exclude_metrics = spec.get("train_exclude_metrics", [])
    train_max_n = spec.get("train_max_n", 1000)
    train_min_n = spec.get("train_min_n", 1)
    
    # Get metric names from prometheus_queries configuration in spec
    prometheus_queries = spec.get("prometheus_queries", [])
    if not prometheus_queries:
        logger.warning("No prometheus_queries found in spec")
        return pd.DataFrame()
    
    # Extract metric names from the configuration
    # Note: ingest function adds "anomstack_" prefix, so we need to match what's in Prometheus
    metric_names = []
    for query_config in prometheus_queries:
        name = query_config.get("name", "")
        if name:
            # Add the prefix that the ingest function uses
            prefixed_name = f"anomstack_{name}"
            metric_names.append(prefixed_name)
    
    logger.info(f"Querying {len(metric_names)} metrics from prometheus_queries config: {metric_names}")
    
    # Combine results from all metrics
    all_dfs = []
    for metric_name in metric_names:
        try:
            df_single = read_sql_prometheus(
                metric_name,
                query_type="query_range",
                start=f"now-{train_metric_timestamp_max_days_ago}d",
                end="now",
                step="300s"  # 5 minute intervals
            )
            if not df_single.empty:
                all_dfs.append(df_single)
        except Exception as e:
            logger.warning(f"Failed to query {metric_name}: {e}")
            continue
    
    # Concatenate all results
    if all_dfs:
        df = pd.concat(all_dfs, ignore_index=True)
    else:
        df = pd.DataFrame()  # Empty DataFrame
    
    if df.empty:
        logger.warning("No data returned from Prometheus train query")
        return df
    
    logger.info(f"Retrieved {len(df)} raw rows from Prometheus")
    
    # Filter out metrics with anomaly detection suffixes
    suffix_pattern = r'_(anomaly_score|alert|llm_alert|threshold_alert)$'
    before_count = len(df)
    df = df[~df["metric_name"].str.contains(suffix_pattern, regex=True, na=False)]
    after_count = len(df)
    logger.info(f"Filtered out {before_count - after_count} rows with anomaly detection suffixes")
    
    # Post-process to match SQL template behavior
    
    # 1. Add required columns
    df["metric_batch"] = metric_batch
    df["metric_type"] = "metric"
    
    # 2. Filter by metric_batch if needed (though Prometheus doesn't store this metadata)
    # For now, assume all metrics belong to the current batch
    
    # 3. Exclude specific metrics if configured
    if train_exclude_metrics:
        excluded_pattern = "|".join(train_exclude_metrics)
        logger.info(f"Excluding metrics matching: {excluded_pattern}")
        df = df[~df["metric_name"].str.contains(excluded_pattern, regex=True, na=False)]
    
    # 4. Group by timestamp and metric_name, then average (like SQL template)
    logger.info("Grouping and averaging metric values")
    grouped_df = df.groupby(["metric_timestamp", "metric_name"], as_index=False)["metric_value"].mean()
    
    # 5. Add metric_recency_rank (like SQL window function)
    logger.info("Adding metric recency ranking")
    grouped_df["metric_recency_rank"] = grouped_df.groupby("metric_name")["metric_timestamp"].rank(
        method="dense", ascending=False
    ).astype(int)
    
    # 6. Apply row limits per metric (like SQL BETWEEN clause)
    logger.info(f"Filtering to ranks between {train_min_n} and {train_max_n}")
    filtered_df = grouped_df[
        (grouped_df["metric_recency_rank"] >= train_min_n) & 
        (grouped_df["metric_recency_rank"] <= train_max_n)
    ].copy()
    
    # 7. Add required columns
    filtered_df["metric_batch"] = metric_batch
    filtered_df["metric_type"] = "metric"
    
    unique_metrics = len(filtered_df["metric_name"].unique()) if len(filtered_df) > 0 else 0
    logger.info(f"Final train dataset: {len(filtered_df)} rows, {unique_metrics} unique metrics")
    return filtered_df 