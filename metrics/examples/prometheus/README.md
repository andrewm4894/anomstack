# Prometheus Infrastructure Monitoring

This **Anomstack metric batch** demonstrates how to monitor infrastructure and application metrics from Prometheus for anomalies. Perfect for DevOps teams, SRE practices, and anyone wanting to detect unusual behavior in their monitoring stack.

## Overview

This example shows how to:
- Integrate Anomstack with existing Prometheus monitoring setups
- Detect anomalies in infrastructure metrics (CPU, memory, network, etc.)
- Set up intelligent alerting that goes beyond simple thresholds
- Apply machine learning to observability data
- Reduce alert fatigue with smarter anomaly detection

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`prometheus.py`](prometheus.py) to query Prometheus HTTP API
2. **Train Job**: PyOD models learn normal patterns in infrastructure metrics
3. **Score Job**: Generate anomaly scores for current system behavior
4. **Alert Job**: Send notifications when unusual infrastructure patterns are detected

### Infrastructure Metrics Monitored
- **System Resources**: CPU usage, memory consumption, disk utilization
- **Application Performance**: Response times, error rates, throughput
- **Network Metrics**: Bandwidth usage, connection counts, latency
- **Custom Business Metrics**: Any metrics exposed to Prometheus

## Files

- **[`prometheus.py`](prometheus.py)**: Custom Python ingest function using Prometheus HTTP API
- **[`prometheus.yaml`](prometheus.yaml)**: Anomstack configuration

## Setup & Usage

### Prerequisites
- Prometheus server running and accessible
- Python `requests` library (usually included with Anomstack)
- Prometheus HTTP API enabled (default on most installations)
- Network access to your Prometheus instance

### Configuration
The YAML file configures:
```yaml
metric_batch: 'prometheus'
ingest_fn: 'prometheus.py'  # Custom Python function
# Recommended: Adjust for infrastructure monitoring needs
alert_threshold: 0.7  # Higher threshold for less noisy infrastructure alerts
train_metric_timestamp_max_days_ago: 30  # Use 30 days of infrastructure data
score_metric_timestamp_max_days_ago: 7   # Score recent week for patterns
```

### Default Demo Setup
This example uses the [Prometheus Labs Demo Server](https://demo.promlabs.com) by default:
- **Endpoint**: `https://demo.promlabs.com/api/v1/query`
- **Sample Metrics**: `demo_memory_usage_bytes`, `demo_cpu_usage_ratio`, `demo_disk_usage_bytes`
- **No Authentication Required**: Perfect for testing and learning

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/prometheus metrics/my_prometheus
   ```

2. **Configure your Prometheus endpoint**: Edit `prometheus.py`:
   ```python
   PROMETHEUS_URL = "http://your-prometheus-server:9090"
   # Or keep default demo server for testing
   PROMETHEUS_URL = "https://demo.promlabs.com"
   ```

3. **Customize metrics to monitor**: Edit the queries in `prometheus.py`:
   ```python
   queries = [
       'node_cpu_seconds_total',
       'node_memory_MemAvailable_bytes', 
       'prometheus_http_requests_total',
       'your_custom_metric_name'
   ]
   ```

4. **Enable in Dagster**: The jobs will appear in your Dagster UI

### Production Configuration Examples

#### Monitor Node Exporter Metrics
```python
queries = [
    'node_cpu_seconds_total{mode="idle"}',
    'node_memory_MemAvailable_bytes',
    'node_filesystem_avail_bytes{mountpoint="/"}',
    'node_network_receive_bytes_total',
    'node_load1'
]
```

#### Monitor Application Metrics
```python
queries = [
    'http_requests_total',
    'http_request_duration_seconds',
    'database_connections_active',
    'queue_size',
    'error_rate'
]
```

#### Monitor Kubernetes Cluster
```python
queries = [
    'kube_pod_status_ready',
    'kube_deployment_status_replicas',
    'container_cpu_usage_seconds_total',
    'container_memory_usage_bytes',
    'kube_node_status_condition'
]
```

## Example Output

The ingest function returns Prometheus data like:
```python
[
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'demo_memory_usage_bytes',
        'metric_value': 8589934592.0
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'demo_cpu_usage_ratio',
        'metric_value': 0.75
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'demo_disk_usage_bytes',
        'metric_value': 42949672960.0
    }
]
```

## Infrastructure Anomaly Detection Scenarios

This example can detect:
- **Resource Exhaustion**: Unusual spikes in CPU, memory, or disk usage
- **Performance Degradation**: Response time anomalies beyond normal variation
- **Application Errors**: Error rate spikes that don't match typical patterns
- **Network Issues**: Bandwidth or latency anomalies
- **Service Disruptions**: Availability metrics showing unusual patterns
- **Capacity Planning**: Growth trends that deviate from predictions
- **Security Incidents**: Unusual access patterns or resource consumption

## DevOps & SRE Use Cases

### Intelligent Alerting
- Replace static thresholds with ML-based anomaly detection
- Reduce false positives by learning normal operational patterns
- Context-aware alerts that consider time-of-day and seasonal patterns

### Incident Prevention
- Early warning system for developing issues
- Detect cascading failures before they impact users
- Identify resource constraints before they cause outages

### Performance Optimization
- Identify performance anomalies that suggest optimization opportunities
- Detect when services deviate from baseline performance
- Monitor the impact of deployments on system behavior

### Capacity Planning
- Detect when growth patterns change unexpectedly
- Identify resources approaching capacity limits
- Plan scaling based on anomaly patterns rather than simple projections

## Integration with Anomstack Features

- **Dashboard**: Visualize infrastructure metrics and anomaly scores in real-time
- **Alerts**: Get Slack/email notifications for infrastructure anomalies
- **Change Detection**: Identify when system behavior fundamentally changes
- **LLM Alerts**: Use AI to analyze and explain complex infrastructure anomalies
- **Multi-frequency**: Monitor at different intervals (1min, 5min, 1hour)

## Environment Variables

Configure Prometheus-specific settings:
```bash
# Prometheus server configuration
PROMETHEUS_URL="http://prometheus:9090"
PROMETHEUS_USERNAME="admin"  # If authentication required
PROMETHEUS_PASSWORD="secret"

# Custom query timeout and step interval
PROMETHEUS_TIMEOUT=30
PROMETHEUS_STEP="60s"

# Metric filtering
PROMETHEUS_METRICS="node_cpu,node_memory,http_requests"  # Comma-separated prefixes
```

## API Integration Details

**Prometheus HTTP API Endpoints Used**:
- **Instant Queries**: `/api/v1/query?query={metric_name}`
- **Range Queries**: `/api/v1/query_range?query={metric_name}&start={start}&end={end}&step={step}`

**Query Examples**:
```python
# Simple metric query
query = "node_cpu_seconds_total"

# Aggregated query
query = "avg(node_cpu_seconds_total) by (instance)"

# Rate calculation  
query = "rate(http_requests_total[5m])"

# Complex PromQL
query = "100 - (avg(node_memory_MemAvailable_bytes) / avg(node_memory_MemTotal_bytes) * 100)"
```

## Advanced Features

### Custom PromQL Queries
```python
# Application-specific SLI monitoring
queries = {
    'availability_sli': '(sum(rate(http_requests_total{status!~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100',
    'latency_sli': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))',
    'error_budget': '(1 - (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])))) * 100'
}
```

### Multi-Dimensional Metrics
```python
# Handle Prometheus labels and dimensions
def process_prometheus_response(response):
    metrics = []
    for result in response['data']['result']:
        labels = result['metric']
        value = float(result['value'][1])
        
        # Create metric name from labels
        metric_name = f"{labels.get('__name__', 'unknown')}"
        if 'instance' in labels:
            metric_name += f"_{labels['instance'].replace('.', '_').replace(':', '_')}"
            
        metrics.append({
            'metric_timestamp': datetime.now(),
            'metric_name': metric_name,
            'metric_value': value
        })
    return metrics
```

### Authentication & Security
```python
# Handle Prometheus authentication
import requests
from requests.auth import HTTPBasicAuth

def query_prometheus(query, auth=None):
    headers = {'Accept': 'application/json'}
    
    if auth:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={'query': query},
            auth=HTTPBasicAuth(auth['username'], auth['password']),
            headers=headers
        )
    else:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={'query': query},
            headers=headers
        )
    
    return response.json()
```

This example provides a powerful foundation for applying machine learning-based anomaly detection to your existing Prometheus monitoring infrastructure, enabling more intelligent and proactive system monitoring.
