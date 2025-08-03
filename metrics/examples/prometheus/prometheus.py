def ingest():
    """
    Ingest data from the Prometheus demo API using the requests library.
    Retrieves 10 interesting metrics and returns a DataFrame with columns:
    metric_timestamp, metric_name, metric_value.
    The metric_timestamp is aggregated to the second level and duplicates are removed.
    """
    from dagster import get_dagster_logger
    import pandas as pd
    import requests

    logger = get_dagster_logger()

    # Define 10 queries with a friendly label and corresponding PromQL query.
    queries = [
        ("demo_api_http_requests_in_progress", "demo_api_http_requests_in_progress"),
        (
            "avg_api_request_duration",
            "rate(demo_api_request_duration_seconds_sum[5m]) / rate(demo_api_request_duration_seconds_count[5m])",
        ),
        ("cpu_usage_rate", "rate(demo_cpu_usage_seconds_total[5m])"),
        ("demo_memory_usage_bytes", "demo_memory_usage_bytes"),
        ("demo_batch_last_run_duration_seconds", "demo_batch_last_run_duration_seconds"),
        ("demo_disk_usage_bytes", "demo_disk_usage_bytes"),
        ("demo_disk_total_bytes", "demo_disk_total_bytes"),
        ("items_shipped_rate", "rate(demo_items_shipped_total[5m])"),
        ("demo_intermittent_metric", "demo_intermittent_metric"),
        ("demo_is_holiday", "demo_is_holiday"),
    ]

    base_url = "https://demo.promlabs.com/api/v1/query"
    all_rows = []

    for label, query in queries:
        params = {"query": query}
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from {base_url} with query '{query}': {e}")
            continue

        result = response.json()
        if result.get("status") != "success":
            logger.error(f"Query '{query}' did not succeed: {result}")
            continue

        # Process each time series returned in the result.
        for item in result.get("data", {}).get("result", []):
            # Each item should contain a "value": [timestamp, value]
            value_arr = item.get("value", [])
            if len(value_arr) != 2:
                continue

            timestamp_str, value_str = value_arr
            try:
                # Convert the Prometheus timestamp (seconds since epoch) to a datetime,
                # and floor it to the nearest second.
                ts = pd.to_datetime(float(timestamp_str), unit="s").floor("S")
            except Exception as ex:
                logger.error(f"Error converting timestamp {timestamp_str}: {ex}")
                ts = pd.Timestamp.utcnow().floor("S")

            try:
                metric_value = float(value_str)
            except (TypeError, ValueError):
                metric_value = None

            # Optionally incorporate instance details in the metric name.
            instance = item.get("metric", {}).get("instance", "")
            metric_name = label
            if instance:
                # Replace colon with underscore to ensure a clean metric name.
                metric_name = f"{label}.{instance.replace(':', '_')}"

            all_rows.append(
                {"metric_timestamp": ts, "metric_name": metric_name, "metric_value": metric_value}
            )

    # Create a DataFrame from the collected rows.
    df = pd.DataFrame(all_rows)

    # Drop duplicates based on the timestamp (to the second) and metric name.
    df = df.drop_duplicates(subset=["metric_timestamp", "metric_name"])
    logger.debug(f"df:\n{df}")

    # Ensure the DataFrame has the expected column order.
    df = df[["metric_timestamp", "metric_name", "metric_value"]]
    return df
