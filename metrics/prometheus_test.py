def ingest():
    """
    Ingest data from Prometheus using node_exporter metrics.

    Returns:
        pd.DataFrame: DataFrame with columns: metric_timestamp, metric_name, metric_value
    """
    import os

    from dagster import get_dagster_logger
    import pandas as pd
    import requests

    logger = get_dagster_logger()

    # Use real node_exporter metrics instead of demo queries
    prometheus_queries = [
        {
            "name": "cpu_usage_percent",
            "query": '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
        },
        {
            "name": "memory_usage_percent",
            "query": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
        },
        {"name": "memory_total_bytes", "query": "node_memory_MemTotal_bytes"},
        {"name": "memory_available_bytes", "query": "node_memory_MemAvailable_bytes"},
        {"name": "load_1m", "query": "node_load1"},
        {"name": "load_5m", "query": "node_load5"},
        {"name": "prometheus_up", "query": "up"},
    ]

    # Configuration from environment variables
    prometheus_query_type = "query_range"
    prometheus_start = "now-1h"
    prometheus_end = "now"
    prometheus_step = "60s"

    logger.info(f"Executing {len(prometheus_queries)} Prometheus queries")

    # Get Prometheus configuration
    config = {
        "host": os.environ.get("ANOMSTACK_PROMETHEUS_HOST", "localhost"),
        "port": os.environ.get("ANOMSTACK_PROMETHEUS_PORT", "9090"),
        "protocol": os.environ.get("ANOMSTACK_PROMETHEUS_PROTOCOL", "http"),
        "username": os.environ.get("ANOMSTACK_PROMETHEUS_USERNAME"),
        "password": os.environ.get("ANOMSTACK_PROMETHEUS_PASSWORD"),
    }

    # Build base URL
    base_url = f"{config['protocol']}://{config['host']}:{config['port']}"

    # Setup authentication if provided
    auth = None
    if config.get("username") and config.get("password"):
        auth = (config["username"], config["password"])

    all_rows = []

    for query_config in prometheus_queries:
        query_name = query_config.get("name", "unnamed_query")
        promql = query_config.get("query", "")

        if not promql:
            logger.warning(f"Empty PromQL query for {query_name}, skipping")
            continue

        try:
            logger.info(f"Executing query '{query_name}': {promql}")

            # Setup endpoint and parameters based on query type
            if prometheus_query_type == "query_range":
                endpoint = "/api/v1/query_range"

                # Convert relative time to Unix timestamps
                import time

                now = int(time.time())

                # Parse start time (e.g., "now-1h" -> 1 hour ago)
                if prometheus_start.startswith("now-"):
                    time_str = prometheus_start.replace("now-", "")
                    if time_str.endswith("h"):
                        hours = int(time_str.replace("h", ""))
                        start_timestamp = now - (hours * 3600)
                    elif time_str.endswith("m"):
                        minutes = int(time_str.replace("m", ""))
                        start_timestamp = now - (minutes * 60)
                    else:
                        start_timestamp = now - 3600  # default 1 hour
                else:
                    start_timestamp = now - 3600  # default 1 hour

                # Parse end time
                if prometheus_end == "now":
                    end_timestamp = now
                else:
                    end_timestamp = now

                params = {
                    "query": promql,
                    "start": str(start_timestamp),
                    "end": str(end_timestamp),
                    "step": prometheus_step,
                }
            else:
                endpoint = "/api/v1/query"
                params = {"query": promql}

            url = base_url + endpoint

            # Execute the query
            response = requests.get(url, params=params, auth=auth, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("status") != "success":
                logger.error(f"Prometheus query failed: {result}")
                continue

            # Process results
            data = result.get("data", {})

            if prometheus_query_type == "query_range":
                # Handle range query results
                for series in data.get("result", []):
                    metric_labels = series.get("metric", {})

                    # Build metric name
                    base_name = promql.split("(")[0].split("{")[0].strip()
                    instance = metric_labels.get("instance", "")
                    if instance:
                        instance = instance.replace(":", "_").replace(".", "_")
                        metric_name = f"{query_name}.{base_name}.{instance}"
                    else:
                        metric_name = f"{query_name}.{base_name}"

                    for timestamp_val, value_str in series.get("values", []):
                        try:
                            ts = pd.to_datetime(float(timestamp_val), unit="s").floor("S")
                            metric_value = float(value_str)

                            all_rows.append(
                                {
                                    "metric_timestamp": ts,
                                    "metric_name": metric_name,
                                    "metric_value": metric_value,
                                }
                            )
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Error parsing value {value_str}: {e}")
                            continue
            else:
                # Handle instant query results
                for series in data.get("result", []):
                    metric_labels = series.get("metric", {})

                    # Build metric name
                    base_name = promql.split("(")[0].split("{")[0].strip()
                    instance = metric_labels.get("instance", "")
                    if instance:
                        instance = instance.replace(":", "_").replace(".", "_")
                        metric_name = f"{query_name}.{base_name}.{instance}"
                    else:
                        metric_name = f"{query_name}.{base_name}"

                    value_arr = series.get("value", [])
                    if len(value_arr) == 2:
                        timestamp_val, value_str = value_arr
                        try:
                            ts = pd.to_datetime(float(timestamp_val), unit="s").floor("S")
                            metric_value = float(value_str)

                            all_rows.append(
                                {
                                    "metric_timestamp": ts,
                                    "metric_name": metric_name,
                                    "metric_value": metric_value,
                                }
                            )
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Error parsing value {value_str}: {e}")
                            continue

        except Exception as e:
            logger.error(f"Error executing query '{query_name}': {e}")
            continue

    # Create DataFrame from results
    if all_rows:
        df = pd.DataFrame(all_rows)
        df = df.drop_duplicates(subset=["metric_timestamp", "metric_name"])
        logger.info(f"Retrieved {len(df)} total rows from Prometheus")
        return df
    else:
        logger.warning("No successful queries, returning empty DataFrame")
        return pd.DataFrame(columns=["metric_timestamp", "metric_name", "metric_value"])
