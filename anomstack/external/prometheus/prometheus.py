"""
Prometheus integration for Anomstack.

This module provides functions for reading from and writing to Prometheus instances,
supporting both PromQL queries for reading and remote write API for sending data.
"""

import os
import struct
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

from dagster import get_dagster_logger
import pandas as pd
import requests

# Add imports for Protocol Buffers and Prometheus client
try:
    from prometheus_client import parser
    from prometheus_client.core import CollectorRegistry, Gauge
    from prometheus_client.exposition import generate_latest
    import snappy

    PROTOBUF_AVAILABLE = True
    IMPORT_ERROR = None
except ImportError as e:
    PROTOBUF_AVAILABLE = False
    IMPORT_ERROR = str(e)


def get_prometheus_config() -> Dict[str, Optional[str]]:
    """
    Get Prometheus connection configuration from environment variables.

    Returns:
        Dict containing Prometheus connection parameters
    """
    return {
        "host": os.environ.get("ANOMSTACK_PROMETHEUS_HOST", "localhost"),
        "port": os.environ.get("ANOMSTACK_PROMETHEUS_PORT", "9090"),
        "protocol": os.environ.get("ANOMSTACK_PROMETHEUS_PROTOCOL", "http"),
        "username": os.environ.get("ANOMSTACK_PROMETHEUS_USERNAME"),
        "password": os.environ.get("ANOMSTACK_PROMETHEUS_PASSWORD"),
        "remote_write_url": os.environ.get("ANOMSTACK_PROMETHEUS_REMOTE_WRITE_URL"),
    }


def build_prometheus_url(config: Dict[str, Optional[str]], endpoint: str = "") -> str:
    """
    Build Prometheus URL from configuration.

    Args:
        config: Prometheus configuration dict
        endpoint: API endpoint to append

    Returns:
        Complete Prometheus URL
    """
    base_url = f"{config['protocol']}://{config['host']}:{config['port']}"
    return urljoin(base_url, endpoint)


def get_prometheus_auth(config: Dict[str, Optional[str]]) -> Optional[tuple]:
    """
    Get authentication tuple for Prometheus requests.

    Args:
        config: Prometheus configuration dict

    Returns:
        Authentication tuple or None
    """
    if config.get("username") and config.get("password"):
        return (config["username"], config["password"])
    return None


def read_sql_prometheus(promql: str, **kwargs) -> pd.DataFrame:
    """
    Read data from Prometheus using PromQL query.

    Note: This function is named read_sql_prometheus to match the pattern used by other
    database integrations, but it actually executes PromQL queries, not SQL.

    Args:
        promql: PromQL query string
        **kwargs: Additional parameters like time range, step, etc.

    Returns:
        pd.DataFrame: Query results with columns: metric_timestamp, metric_name, metric_value
    """
    logger = get_dagster_logger()
    config = get_prometheus_config()

    # Default to instant query, but support range queries
    query_type = kwargs.get("query_type", "query")  # "query" or "query_range"

    if query_type == "query_range":
        endpoint = "/api/v1/query_range"
        params = {
            "query": promql,
            "start": kwargs.get("start", "now-1h"),
            "end": kwargs.get("end", "now"),
            "step": kwargs.get("step", "60s"),
        }
    else:
        endpoint = "/api/v1/query"
        params = {"query": promql}

    url = build_prometheus_url(config, endpoint)
    auth = get_prometheus_auth(config)

    logger.info(f"Executing PromQL query: {promql}")
    logger.debug(f"Prometheus URL: {url}")

    try:
        response = requests.get(url, params=params, auth=auth, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to query Prometheus at {url}: {e}")
        raise

    result = response.json()
    if result.get("status") != "success":
        logger.error(f"Prometheus query failed: {result}")
        raise RuntimeError(f"Prometheus query failed: {result.get('error', 'Unknown error')}")

    # Convert Prometheus response to standard DataFrame format
    all_rows = []
    data = result.get("data", {})

    if query_type == "query_range":
        # Handle range query results
        for series in data.get("result", []):
            metric_labels = series.get("metric", {})
            metric_name = _build_metric_name(promql, metric_labels)

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
            metric_name = _build_metric_name(promql, metric_labels)

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

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["metric_timestamp", "metric_name"])

    logger.info(f"Retrieved {len(df)} rows from Prometheus")
    return df


def _build_metric_name(promql: str, metric_labels: Dict) -> str:
    """
    Build a readable metric name from PromQL query and labels.

    Args:
        promql: Original PromQL query
        metric_labels: Metric labels dict

    Returns:
        String metric name
    """
    # Try to extract base metric name from PromQL
    base_name = promql.split("(")[0].split("{")[0].strip()

    # Add instance info if available
    instance = metric_labels.get("instance", "")
    if instance:
        # Clean up instance name
        instance = instance.replace(":", "_").replace(".", "_")
        return f"{base_name}.{instance}"

    # Add other relevant labels
    job = metric_labels.get("job", "")
    if job:
        return f"{base_name}.{job}"

    return base_name


def save_df_prometheus(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    """
    Save DataFrame to Prometheus using remote write API with proper Protocol Buffers format.

    Args:
        df: DataFrame with columns: metric_timestamp, metric_name, metric_value
        table_key: Not used for Prometheus, but kept for interface consistency

    Returns:
        pd.DataFrame: The input DataFrame
    """
    logger = get_dagster_logger()
    config = get_prometheus_config()

    remote_write_url = config.get("remote_write_url")
    if not remote_write_url:
        logger.warning(
            "No ANOMSTACK_PROMETHEUS_REMOTE_WRITE_URL configured, skipping Prometheus write"
        )
        return df

    if not PROTOBUF_AVAILABLE:
        logger.error(f"Missing dependencies: {IMPORT_ERROR}")
        logger.error("Required: pip install protobuf python-snappy")
        logger.warning("Skipping Prometheus write - install required packages")
        return df

    logger.info(f"Saving {len(df)} rows to Prometheus via remote write")
    logger.debug(f"PROTOBUF_AVAILABLE: {PROTOBUF_AVAILABLE}")
    logger.debug(f"Remote write URL: {remote_write_url}")

    # Convert DataFrame to Prometheus remote write format
    time_series = _convert_df_to_prometheus_format(df)

    if not time_series:
        logger.warning("No valid time series data to write to Prometheus")
        return df

    try:
        # Create proper Protocol Buffers message
        logger.debug(f"Creating protobuf message for {len(time_series)} time series")
        write_request = _create_protobuf_write_request(time_series)
        logger.debug(f"Protobuf message size: {len(write_request)} bytes")

        # Compress with Snappy
        compressed_data = snappy.compress(write_request)
        logger.debug(f"Compressed size: {len(compressed_data)} bytes")

        # Send to Prometheus remote write endpoint
        auth = get_prometheus_auth(config)
        headers = {
            "Content-Type": "application/x-protobuf",
            "Content-Encoding": "snappy",
            "X-Prometheus-Remote-Write-Version": "0.1.0",
        }
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Auth: {auth is not None}")

        # Debug: Log sample timestamps to check for "out of bounds" issues
        if time_series:
            sample_ts = time_series[0]
            if sample_ts.get("samples"):
                sample_timestamp = sample_ts["samples"][0]["timestamp"]
                import time as time_module

                current_time_ms = int(time_module.time() * 1000)
                logger.debug(
                    f"Sample timestamp: {sample_timestamp}, Current time: {current_time_ms}, Diff: {current_time_ms - sample_timestamp}ms"
                )

        response = requests.post(
            remote_write_url, data=compressed_data, headers=headers, auth=auth, timeout=30
        )
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Response text: {response.text}")
        response.raise_for_status()
        logger.info(f"✅ Successfully wrote {len(time_series)} time series to Prometheus")

    except Exception as e:
        logger.error(f"Failed to write to Prometheus remote write endpoint: {e}")
        logger.warning("Continuing without writing to Prometheus")

    return df


def _convert_df_to_prometheus_format(df: pd.DataFrame) -> List[Dict]:
    """
    Convert DataFrame to Prometheus remote write time series format.

    Args:
        df: DataFrame with metric data

    Returns:
        List of time series dictionaries
    """
    logger = get_dagster_logger()
    time_series = []

    # Group by metric name to create separate time series
    for metric_name, group in df.groupby("metric_name"):
        try:
            # Parse metric name and add suffix based on metric_type
            metric_name_str = str(metric_name)
            
            # Add suffix based on metric_type if present
            if "metric_type" in group.columns:
                metric_type = group["metric_type"].iloc[0]  # All rows in group should have same type
                if metric_type == "score":
                    metric_name_str = f"{metric_name_str}_anomaly_score"
                elif metric_type == "alert":
                    metric_name_str = f"{metric_name_str}_alert"
                elif metric_type == "llmalert":
                    metric_name_str = f"{metric_name_str}_llm_alert"
                elif metric_type == "tholdalert":
                    metric_name_str = f"{metric_name_str}_threshold_alert"
                # metric_type == "metric" keeps original name (no suffix)
            
            labels = {"__name__": metric_name_str}

            # If metric name contains dots, use the parts as labels
            if "." in metric_name_str:
                parts = metric_name_str.split(".")
                labels["__name__"] = parts[0]
                if len(parts) > 1:
                    labels["instance"] = ".".join(parts[1:])

            # Create samples from the group
            samples = []
            # Use current timestamp to avoid "out of bounds" errors
            # Prometheus typically rejects samples older than 1 hour or in the future
            current_time_ms = int(time.time() * 1000)

            # Sort group by timestamp to ensure chronological order
            sorted_group = group.sort_values('metric_timestamp')
            
            for _, row in sorted_group.iterrows():
                try:
                    value = float(row["metric_value"])
                    
                    # Use the actual metric timestamp, not current time
                    timestamp_ms = current_time_ms  # Default fallback
                    try:
                        metric_ts = row.get("metric_timestamp")
                        if metric_ts is not None and not pd.isna(metric_ts):
                            # Convert to timestamp milliseconds
                            if hasattr(metric_ts, 'timestamp'):
                                # Already a datetime object
                                timestamp_ms = int(metric_ts.timestamp() * 1000)
                            else:
                                # Convert to datetime first
                                dt = pd.to_datetime(metric_ts)  
                                timestamp_ms = int(dt.timestamp() * 1000)
                    except (ValueError, TypeError, AttributeError):
                        # Use fallback timestamp if conversion fails
                        pass

                    samples.append({"timestamp": timestamp_ms, "value": value})
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Error processing row for metric {metric_name_str}: {e}")
                    continue

            if samples:
                time_series.append(
                    {
                        "labels": [{"name": k, "value": v} for k, v in labels.items()],
                        "samples": samples,
                    }
                )

        except Exception as e:
            logger.warning(f"Error processing metric {metric_name}: {e}")
            continue

    return time_series


def _create_protobuf_write_request(time_series: List[Dict]) -> bytes:
    """
    Create a Protocol Buffers WriteRequest message for Prometheus remote write.

    This manually creates the protobuf binary format without requiring .proto compilation.
    Based on the Prometheus remote.proto specification.
    """
    logger = get_dagster_logger()

    # Build WriteRequest protobuf message manually
    # WriteRequest { repeated TimeSeries timeseries = 1; }
    write_request_data = b""

    for ts in time_series:
        # Create TimeSeries message
        timeseries_data = b""

        # Add labels (field 1, repeated Label)
        for label in ts.get("labels", []):
            label_data = b""
            # Label { string name = 1; string value = 2; }
            label_data += _encode_protobuf_string(1, str(label["name"]))
            label_data += _encode_protobuf_string(2, str(label["value"]))
            timeseries_data += _encode_protobuf_message(1, label_data)

        # Add samples (field 2, repeated Sample)
        for sample in ts.get("samples", []):
            sample_data = b""
            # Sample { double value = 1; int64 timestamp = 2; }
            sample_data += _encode_protobuf_double(1, float(sample["value"]))
            sample_data += _encode_protobuf_int64(2, int(sample["timestamp"]))
            timeseries_data += _encode_protobuf_message(2, sample_data)

        # Add TimeSeries to WriteRequest (field 1, repeated)
        write_request_data += _encode_protobuf_message(1, timeseries_data)

    logger.debug(f"Created protobuf WriteRequest with {len(time_series)} time series")
    return write_request_data


def _encode_protobuf_string(field_number: int, value: str) -> bytes:
    """Encode a protobuf string field."""
    value_bytes = value.encode("utf-8")
    length = len(value_bytes)
    field_header = (field_number << 3) | 2  # Wire type 2 for length-delimited
    return _encode_varint(field_header) + _encode_varint(length) + value_bytes


def _encode_protobuf_double(field_number: int, value: float) -> bytes:
    """Encode a protobuf double field."""
    field_header = (field_number << 3) | 1  # Wire type 1 for 64-bit
    return _encode_varint(field_header) + struct.pack("<d", value)


def _encode_protobuf_int64(field_number: int, value: int) -> bytes:
    """Encode a protobuf int64 field."""
    field_header = (field_number << 3) | 0  # Wire type 0 for varint
    return _encode_varint(field_header) + _encode_varint(value)


def _encode_protobuf_message(field_number: int, message_data: bytes) -> bytes:
    """Encode a protobuf message field."""
    field_header = (field_number << 3) | 2  # Wire type 2 for length-delimited
    return _encode_varint(field_header) + _encode_varint(len(message_data)) + message_data


def _encode_varint(value: int) -> bytes:
    """Encode a variable-length integer."""
    result = b""
    while value >= 0x80:
        result += bytes([value & 0x7F | 0x80])
        value >>= 7
    result += bytes([value & 0x7F])
    return result


def execute_promql_queries(queries: List[Dict[str, str]], **kwargs) -> pd.DataFrame:
    """
    Execute multiple PromQL queries and return combined results.

    This function is designed to be used from YAML-configured metric batches.

    Args:
        queries: List of dicts with "name" and "query" keys
        **kwargs: Additional query parameters

    Returns:
        pd.DataFrame: Combined results from all queries
    """
    logger = get_dagster_logger()
    all_rows = []

    for query_config in queries:
        query_name = query_config.get("name", "unnamed_query")
        promql = query_config.get("query", "")

        if not promql:
            logger.warning(f"Empty PromQL query for {query_name}, skipping")
            continue

        try:
            logger.info(f"Executing query '{query_name}': {promql}")
            df = read_sql_prometheus(promql, **kwargs)

            # Prefix metric names with query name for clarity
            df["metric_name"] = df["metric_name"].apply(lambda x: f"{query_name}.{x}")

            all_rows.append(df)

        except Exception as e:
            logger.error(f"Error executing query '{query_name}': {e}")
            continue

    if all_rows:
        combined_df = pd.concat(all_rows, ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["metric_timestamp", "metric_name"])
        return combined_df
    else:
        logger.warning("No successful queries, returning empty DataFrame")
        return pd.DataFrame(columns=["metric_timestamp", "metric_name", "metric_value"])
