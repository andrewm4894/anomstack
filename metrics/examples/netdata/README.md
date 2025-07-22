# Netdata System Monitoring

This **Anomstack metric batch** demonstrates how to monitor real-time system metrics using Netdata's powerful API for anomaly detection. Perfect for system administrators, DevOps engineers, and anyone wanting to detect unusual system behavior across their infrastructure.

## Overview

This example shows how to:
- Integrate with Netdata's real-time monitoring API
- Monitor comprehensive system metrics (CPU, memory, network, disk, etc.)
- Detect anomalies in system performance and resource usage
- Set up intelligent alerts for infrastructure issues
- Scale monitoring across multiple Netdata instances

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`netdata.py`](netdata.py) to query Netdata's REST API
2. **Train Job**: PyOD models learn normal patterns in system metrics
3. **Score Job**: Generate anomaly scores for current system behavior
4. **Alert Job**: Send notifications when unusual system patterns are detected

### System Metrics Monitored
- **CPU Usage**: Per-core utilization, load averages, context switches
- **Memory**: RAM usage, swap utilization, buffer/cache metrics
- **Network**: Traffic, packet rates, connection states, interface statistics
- **Disk I/O**: Read/write operations, throughput, queue depths
- **System**: Process counts, file descriptor usage, uptime metrics

## Files

- **[`netdata.py`](netdata.py)**: Custom Python ingest function using Netdata REST API
- **[`netdata.yaml`](netdata.yaml)**: Anomstack configuration

## Setup & Usage

### Prerequisites
- Netdata installed and running on target systems
- Network access to Netdata instances (default port 19999)
- Python `requests` library (included with Anomstack)
- Netdata API access enabled (default configuration)

### Configuration
The YAML file configures:
```yaml
metric_batch: 'netdata'
ingest_fn: 'netdata.py'  # Custom Python function
# Recommended: Adjust for system monitoring needs
alert_threshold: 0.75  # Higher threshold for less noisy system alerts
train_metric_timestamp_max_days_ago: 14  # Use 2 weeks of system data
score_metric_timestamp_max_days_ago: 3   # Score recent 3 days for patterns
```

### Default Demo Setup
This example uses Netdata's public demo servers by default:
- **London Server**: `https://london.my-netdata.io`
- **Atlanta Server**: `https://atlanta.my-netdata.io`
- **Demo Charts**: `system.cpu`, `system.ram`, `system.net`, `system.io`
- **No Authentication Required**: Perfect for testing and learning

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/netdata metrics/my_netdata
   ```

2. **Configure your Netdata endpoints**: Edit `netdata.py`:
   ```python
   # Your own Netdata instances
   NETDATA_HOSTS = [
       "http://server1:19999",
       "http://server2:19999",
       "http://monitoring.company.com:19999"
   ]
   # Or keep demo servers for testing
   NETDATA_HOSTS = [
       "https://london.my-netdata.io",
       "https://atlanta.my-netdata.io"
   ]
   ```

3. **Customize metrics to monitor**: Edit the charts in `netdata.py`:
   ```python
   CHARTS_TO_MONITOR = [
       'system.cpu',      # CPU utilization
       'system.ram',      # Memory usage
       'system.net',      # Network traffic
       'system.io',       # Disk I/O
       'system.load',     # System load
       'apps.cpu',        # Per-app CPU usage
       'users.cpu'        # Per-user CPU usage
   ]
   ```

4. **Enable in Dagster**: The jobs will appear in your Dagster UI

### Production Configuration Examples

#### Monitor Web Server Farm
```python
NETDATA_HOSTS = [
    "http://web01.company.com:19999",
    "http://web02.company.com:19999",
    "http://web03.company.com:19999",
    "http://load-balancer.company.com:19999"
]

CHARTS_TO_MONITOR = [
    'system.cpu',
    'system.ram',
    'nginx.requests',
    'nginx.connections',
    'web_log.response_codes'
]
```

#### Monitor Database Cluster
```python
NETDATA_HOSTS = [
    "http://db-master:19999",
    "http://db-replica1:19999",
    "http://db-replica2:19999"
]

CHARTS_TO_MONITOR = [
    'mysql.queries',
    'mysql.connections',
    'mysql.innodb_io',
    'system.cpu',
    'system.ram',
    'system.io'
]
```

#### Monitor Kubernetes Nodes
```python
NETDATA_HOSTS = [
    "http://k8s-node01:19999",
    "http://k8s-node02:19999",
    "http://k8s-node03:19999"
]

CHARTS_TO_MONITOR = [
    'k8s.cluster_cpu_usage',
    'k8s.cluster_memory_usage',
    'k8s.pods_running',
    'k8s.containers_running',
    'system.cpu',
    'system.ram'
]
```

## Example Output

The ingest function returns Netdata metrics like:
```python
[
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'london_system_cpu_user',
        'metric_value': 45.2
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'london_system_ram_used_percent',
        'metric_value': 78.5
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'atlanta_system_net_received_mbps',
        'metric_value': 125.7
    }
]
```

## System Anomaly Detection Scenarios

This example can detect:
- **Resource Exhaustion**: CPU, memory, or disk usage spikes beyond normal patterns
- **Performance Degradation**: Response time increases or throughput drops
- **Network Issues**: Unusual traffic patterns, packet loss, or connection problems
- **Application Errors**: Process crashes, service failures, or error rate increases
- **Security Incidents**: Unusual process behavior or resource consumption patterns
- **Hardware Issues**: Disk errors, network interface problems, or thermal events
- **Capacity Planning**: Resource usage trending beyond normal growth patterns

## DevOps & System Administration Use Cases

### Proactive Monitoring
- Early warning system for developing system issues
- Detect cascading failures before they impact services
- Identify resource bottlenecks before they cause outages

### Performance Optimization
- Identify performance anomalies suggesting optimization opportunities
- Detect when applications deviate from baseline performance
- Monitor the impact of deployments on system resources

### Infrastructure Management
- Track resource utilization across server farms
- Monitor the health of distributed systems
- Detect when servers need maintenance or replacement

### Security Monitoring
- Identify unusual resource consumption patterns
- Detect potential security incidents through system behavior
- Monitor for unauthorized process execution

## Integration with Anomstack Features

- **Dashboard**: Visualize system metrics and anomaly scores in real-time
- **Alerts**: Get Slack/email notifications for system anomalies
- **Change Detection**: Identify when system behavior fundamentally changes
- **LLM Alerts**: Use AI to analyze and explain complex system anomalies
- **Multi-frequency**: Monitor at different intervals (30s, 1min, 5min)

## Environment Variables

Configure Netdata-specific settings:
```bash
# Netdata server configuration
NETDATA_HOSTS="http://server1:19999,http://server2:19999"
NETDATA_USERNAME="admin"      # If authentication enabled
NETDATA_PASSWORD="secret"

# API request configuration
NETDATA_TIMEOUT=30
NETDATA_AFTER_SECONDS=-600    # Look back 10 minutes
NETDATA_POINTS=1              # Single data point per request

# Chart filtering
NETDATA_CHARTS="system.cpu,system.ram,system.net"  # Comma-separated
```

## API Integration Details

**Netdata API Endpoints Used**:
- **Data API**: `/api/v1/data?chart={chart}&after={after}&before={before}&points={points}`
- **Charts API**: `/api/v1/charts` (to discover available charts)
- **Info API**: `/api/v1/info` (to get system information)

**Example API Calls**:
```python
# Get current CPU usage
"https://server:19999/api/v1/data?chart=system.cpu&after=-600&before=0&points=1"

# Get network traffic over last hour
"https://server:19999/api/v1/data?chart=system.net&after=-3600&before=0&points=60"

# Get memory usage with specific dimensions
"https://server:19999/api/v1/data?chart=system.ram&dimensions=used&after=-300&points=1"
```

**Response Format**:
```json
{
  "api": 1,
  "id": "system.cpu",
  "name": "system.cpu",
  "view_update_every": 1,
  "update_every": 1,
  "first_entry": 1609459200,
  "last_entry": 1609459800,
  "dimension_names": ["guest_nice", "guest", "steal", "softirq", "irq", "user", "system", "nice", "iowait", "idle"],
  "dimension_ids": ["guest_nice", "guest", "steal", "softirq", "irq", "user", "system", "nice", "iowait", "idle"],
  "data": [
    [1609459800, 0, 0, 0, 0.5025, 0, 12.0603, 2.5125, 0, 0, 84.9246]
  ]
}
```

## Advanced Features

### Multi-Host Aggregation
```python
# Aggregate metrics across multiple hosts
def aggregate_metrics(hosts, chart):
    total_cpu = 0
    host_count = 0

    for host in hosts:
        data = get_netdata_metric(host, chart)
        if data:
            total_cpu += extract_cpu_usage(data)
            host_count += 1

    return {
        'metric_timestamp': datetime.now(),
        'metric_name': f'cluster_avg_{chart}',
        'metric_value': total_cpu / host_count if host_count > 0 else 0
    }
```

### Custom Chart Discovery
```python
# Automatically discover available charts
def discover_charts(netdata_host):
    response = requests.get(f"{netdata_host}/api/v1/charts")
    charts = response.json()

    # Filter for interesting charts
    system_charts = [
        chart_id for chart_id, chart_info in charts['charts'].items()
        if chart_id.startswith(('system.', 'apps.', 'users.'))
    ]

    return system_charts
```

### Authentication & Security
```python
# Handle Netdata authentication if enabled
def get_netdata_data(host, chart, auth=None):
    url = f"{host}/api/v1/data"
    params = {
        'chart': chart,
        'after': -600,
        'before': 0,
        'points': 1
    }

    if auth:
        response = requests.get(url, params=params, auth=auth)
    else:
        response = requests.get(url, params=params)

    return response.json()
```

### Error Handling & Resilience
```python
# Robust error handling for production use
def safe_netdata_request(host, chart, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(
                f"{host}/api/v1/data",
                params={'chart': chart, 'after': -300, 'points': 1},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                logger.error(f"Failed to get data from {host}: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Netdata Configuration Optimization

### High-Frequency Collection
```bash
# /etc/netdata/netdata.conf
[global]
    update every = 1          # Collect every second
    memory mode = ram         # Keep data in RAM for speed
    history = 3600           # Keep 1 hour of data
```

### Custom Alarms Integration
```bash
# /etc/netdata/health.d/anomstack.conf
template: anomstack_cpu_high
      on: system.cpu
   lookup: average -300
    units: %
    every: 60s
     warn: $this > 80
     crit: $this > 95
     info: CPU usage is high - Anomstack will detect patterns
```

This example provides a comprehensive foundation for real-time system monitoring and anomaly detection using Netdata's rich metrics ecosystem with Anomstack's machine learning capabilities.
