"""
Parameterized Prometheus ingest function for Anomstack.

This version reads configuration from YAML instead of hardcoded values,
making it more flexible and reusable.
"""

from dagster import get_dagster_logger

from anomstack.external.prometheus.prometheus import execute_promql_queries


def ingest(
    prometheus_queries=None,
    prometheus_query_type="query",
    prometheus_start="now-1h",
    prometheus_end="now",
    prometheus_step="60s",
    **kwargs,
):
    """
    Ingest data from Prometheus using configurable PromQL queries.

    Args:
        prometheus_queries: List of query configurations with 'name' and 'query' fields
        prometheus_query_type: "query" for instant queries or "query_range" for range queries
        prometheus_start: Start time for range queries (e.g., "now-1h", "2023-01-01T00:00:00Z")
        prometheus_end: End time for range queries (e.g., "now", "2023-01-01T01:00:00Z")
        prometheus_step: Step size for range queries (e.g., "60s", "5m")
        **kwargs: Additional parameters

    Returns:
        pd.DataFrame: DataFrame with columns: metric_timestamp, metric_name, metric_value
    """
    logger = get_dagster_logger()

    # Default queries if none provided (for backward compatibility)
    if not prometheus_queries:
        logger.info("No prometheus_queries provided, using default demo queries")
        prometheus_queries = [
            {
                "name": "demo_api_http_requests_in_progress",
                "query": "demo_api_http_requests_in_progress",
            },
            {
                "name": "avg_api_request_duration",
                "query": "rate(demo_api_request_duration_seconds_sum[5m]) / rate(demo_api_request_duration_seconds_count[5m])",
            },
            {"name": "cpu_usage_rate", "query": "rate(demo_cpu_usage_seconds_total[5m])"},
            {"name": "demo_memory_usage_bytes", "query": "demo_memory_usage_bytes"},
            {
                "name": "demo_batch_last_run_duration_seconds",
                "query": "demo_batch_last_run_duration_seconds",
            },
            {"name": "demo_disk_usage_bytes", "query": "demo_disk_usage_bytes"},
            {"name": "demo_disk_total_bytes", "query": "demo_disk_total_bytes"},
            {"name": "items_shipped_rate", "query": "rate(demo_items_shipped_total[5m])"},
            {"name": "demo_intermittent_metric", "query": "demo_intermittent_metric"},
            {"name": "demo_is_holiday", "query": "demo_is_holiday"},
        ]

    logger.info(f"Executing {len(prometheus_queries)} Prometheus queries")

    # Execute queries using the centralized function
    df = execute_promql_queries(
        queries=prometheus_queries,
        query_type=prometheus_query_type,
        start=prometheus_start,
        end=prometheus_end,
        step=prometheus_step,
    )

    logger.info(f"Retrieved {len(df)} total rows from Prometheus")

    return df
