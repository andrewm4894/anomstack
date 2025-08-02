# Prometheus DB Example

This example demonstrates using **Prometheus as both data source and database destination** for anomaly detection with Anomstack.

## Overview

The `prometheus_db` example:
- **Reads** system metrics from Prometheus using PromQL queries  
- **Writes** anomaly detection results back to Prometheus
- Uses node_exporter metrics for monitoring system performance

This is different from the general `prometheus` example which only reads from Prometheus but can write to any database backend.

## Prerequisites

1. **Prometheus server** running and accessible
2. **node_exporter** running to provide system metrics
3. **Prometheus configured** to scrape node_exporter metrics

## Configuration

### Environment Variables

Set these environment variables for Prometheus connection:

```bash
# Prometheus connection settings
export ANOMSTACK_PROMETHEUS_HOST="localhost"
export ANOMSTACK_PROMETHEUS_PORT="9090" 
export ANOMSTACK_PROMETHEUS_PROTOCOL="http"

# Optional authentication
export ANOMSTACK_PROMETHEUS_USERNAME="your-username"
export ANOMSTACK_PROMETHEUS_PASSWORD="your-password"
```

### Metric Configuration

The example monitors these system metrics:
- **CPU usage percentage** - Calculated from idle time
- **Memory usage percentage** - Available vs total memory
- **Memory total/available bytes** - Raw memory values
- **Load averages** - 1m and 5m system load
- **Prometheus health** - Up/down status

## Usage

1. **Start the metric batch:**
   ```bash
   # Copy to your metrics directory
   cp -r metrics/examples/prometheus_db/ metrics/
   
   # Run with Anomstack
   make local
   ```

2. **Monitor in Dashboard:**
   - View ingested metrics and anomaly scores
   - Check alert status and trends
   - Review system performance patterns

3. **Customize queries:**
   - Edit the `prometheus_queries` in the YAML file
   - Add your own PromQL queries for specific metrics
   - Adjust time ranges and step sizes as needed

## Metrics Generated

Each PromQL query generates metrics with names like:
- `cpu_usage_percent.100.instance_name`
- `memory_usage_percent.1.instance_name` 
- `load_1m.node_load1.instance_name`

## Schedule Configuration

- **Ingest**: Every 5 minutes (`*/5 * * * *`)
- **Training**: Every 3 hours (`*/180 * * * *`)  
- **Scoring**: Every 10 minutes (`*/10 * * * *`)
- **Alerts**: Every 15 minutes (`*/15 * * * *`)

Adjust these schedules based on your monitoring requirements and data volume.

## Troubleshooting

1. **No data ingested**: Check Prometheus connectivity and node_exporter status
2. **Authentication errors**: Verify username/password if using Prometheus auth
3. **Query failures**: Test PromQL queries directly in Prometheus UI
4. **Performance issues**: Reduce query frequency or time ranges

## Related Examples

- `metrics/examples/prometheus/` - Read from Prometheus, write to any DB
- `metrics/examples/netdata/` - Similar system monitoring with Netdata 