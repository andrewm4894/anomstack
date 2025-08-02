# Prometheus Database Integration

This module provides Prometheus integration for Anomstack, enabling both reading metrics from Prometheus via PromQL queries and writing processed results back to Prometheus via the remote write API.

## Features

- **Read from Prometheus**: Execute PromQL queries to retrieve time series data
- **Write to Prometheus**: Send processed metrics back via remote write API
- **Flexible Configuration**: Parameterizable via environment variables and YAML
- **Query Types**: Support for both instant queries and range queries
- **Authentication**: Support for basic authentication
- **Error Handling**: Robust error handling with logging

## Configuration

### Environment Variables

Set these environment variables to configure Prometheus connection:

```bash
# Prometheus server connection
export ANOMSTACK_PROMETHEUS_HOST="localhost"
export ANOMSTACK_PROMETHEUS_PORT="9090"
export ANOMSTACK_PROMETHEUS_PROTOCOL="http"

# Authentication (optional)
export ANOMSTACK_PROMETHEUS_USERNAME="your_username"
export ANOMSTACK_PROMETHEUS_PASSWORD="your_password"

# Remote write endpoint (for saving data back to Prometheus)
export ANOMSTACK_PROMETHEUS_REMOTE_WRITE_URL="http://localhost:9090/api/v1/write"
```

### YAML Configuration

In your metric batch YAML file, specify `db: "prometheus"` to use Prometheus as the database:

```yaml
metric_batch: "my_prometheus_metrics"
db: "prometheus"  # Use Prometheus as database destination

# Prometheus-specific configuration
prometheus_query_type: "query_range"  # or "query" for instant queries
prometheus_start: "now-1h"           # Start time for range queries
prometheus_end: "now"                # End time for range queries
prometheus_step: "60s"               # Step size for range queries

# Define your PromQL queries
prometheus_queries:
  - name: "cpu_usage"
    query: "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"

  - name: "memory_usage"
    query: "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"

  - name: "disk_usage"
    query: "100 - (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100"
```

## Usage Examples

### Reading Data from Prometheus

```python
from anomstack.external.prometheus.prometheus import read_sql_prometheus

# Execute a PromQL query (instant query)
df = read_sql_prometheus("up")

# Execute a range query
df = read_sql_prometheus(
    "rate(http_requests_total[5m])",
    query_type="query_range",
    start="now-1h",
    end="now",
    step="60s"
)
```

### Writing Data to Prometheus

```python
from anomstack.external.prometheus.prometheus import save_df_prometheus
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'metric_timestamp': [pd.Timestamp.now()],
    'metric_name': ['anomaly_score'],
    'metric_value': [0.85]
})

# Save to Prometheus via remote write
save_df_prometheus(df, "anomaly_metrics")
```

### Using with Anomstack Pipeline

```python
from anomstack.external.prometheus.prometheus import execute_promql_queries

def ingest(**kwargs):
    queries = [
        {"name": "cpu_usage", "query": "rate(node_cpu_seconds_total[5m])"},
        {"name": "memory_usage", "query": "node_memory_MemUsed_bytes"}
    ]

    return execute_promql_queries(
        queries=queries,
        query_type="query_range",
        start="now-1h",
        end="now",
        step="60s"
    )
```

## Query Types

### Instant Queries (`query_type: "query"`)
- Returns the current value of metrics at a single point in time
- Best for real-time monitoring and alerting
- Faster execution

### Range Queries (`query_type: "query_range"`)
- Returns time series data over a specified time range
- Better for historical analysis and anomaly detection
- Provides more data points for ML training

## Data Format

All functions return data in Anomstack's standard format:

```python
pd.DataFrame({
    'metric_timestamp': [timestamp],  # pandas.Timestamp
    'metric_name': [name],           # string
    'metric_value': [value]          # float
})
```

## Testing with Local Prometheus

Use the provided Docker Compose setup for local testing:

```bash
# Start Prometheus stack
docker-compose -f docker-compose.prometheus.yaml up -d

# Set environment variables for local testing
export ANOMSTACK_PROMETHEUS_HOST="localhost"
export ANOMSTACK_PROMETHEUS_PORT="9090"
export ANOMSTACK_PROMETHEUS_REMOTE_WRITE_URL="http://localhost:9090/api/v1/write"

# Run your Anomstack pipeline
```

The test setup includes:
- Prometheus server (http://localhost:9090)
- Node Exporter for system metrics (http://localhost:9100)
- Grafana for visualization (http://localhost:3001, admin/admin)
- Demo application with sample metrics (http://localhost:8080)

## Common PromQL Queries

### System Metrics
```yaml
prometheus_queries:
  - name: "cpu_usage_percent"
    query: "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"

  - name: "memory_usage_percent"
    query: "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"

  - name: "disk_usage_percent"
    query: "100 - (node_filesystem_avail_bytes{fstype!=\"tmpfs\"} / node_filesystem_size_bytes{fstype!=\"tmpfs\"}) * 100"

  - name: "network_received_bytes"
    query: "rate(node_network_receive_bytes_total[5m])"
```

### Application Metrics
```yaml
prometheus_queries:
  - name: "http_requests_per_second"
    query: "rate(http_requests_total[5m])"

  - name: "http_request_duration_95th"
    query: "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"

  - name: "error_rate_percent"
    query: "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100"
```

## Limitations

1. **Remote Write Format**: Currently uses JSON format instead of the official Prometheus protobuf format for simplicity
2. **Authentication**: Only basic authentication is supported
3. **Error Handling**: Write failures don't stop the pipeline (by design)

## Troubleshooting

### Connection Issues
- Verify Prometheus is running: `curl http://localhost:9090/api/v1/label/__name__/values`
- Check environment variables: `env | grep ANOMSTACK_PROMETHEUS`
- Verify network connectivity and firewall settings

### Query Issues
- Test PromQL queries in Prometheus UI: http://localhost:9090/graph
- Check query syntax and available metrics: http://localhost:9090/api/v1/label/__name__/values
- Verify time ranges are reasonable (not too large)

### Remote Write Issues
- Ensure remote write is enabled in Prometheus configuration
- Check if the endpoint accepts the format you're sending
- Monitor Prometheus logs for write errors
