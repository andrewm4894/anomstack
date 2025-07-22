# freq

Make use of the `freq` preprocessing param to aggregate to a different frequency than metric is ingested at.

# Frequency Aggregation Example

This **Anomstack metric batch** demonstrates the powerful `freq` preprocessing parameter that allows you to ingest data at one frequency and then aggregate it to a different frequency for training and scoring. Perfect for handling high-frequency data or creating different analytical views of the same metrics.

## Overview

This example shows how to:
- Ingest metrics at high frequency (e.g., every minute)
- Aggregate to lower frequency for anomaly detection (e.g., hourly)
- Use different aggregation methods (mean, sum, max, min)
- Handle time series resampling in Anomstack's preprocessing pipeline
- Optimize model performance by choosing appropriate frequencies

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline with frequency transformation:

1. **Ingest Job**: Collects high-frequency data (e.g., every 1 minute)
2. **Preprocessing**: Automatically resamples data to target frequency (e.g., 1 hour)
3. **Train Job**: PyOD models train on aggregated data for more stable patterns
4. **Score Job**: Generate anomaly scores on aggregated time series
5. **Alert Job**: Send notifications based on aggregated anomaly patterns

### Why Use Frequency Aggregation?

#### Noise Reduction
- High-frequency data often contains noise that can confuse anomaly detection
- Aggregation smooths out short-term fluctuations to reveal true patterns
- Focus on meaningful trends rather than momentary spikes

#### Performance Optimization  
- Reduce data volume for faster model training
- Lower memory requirements for large time series
- More efficient computation with aggregated data

#### Pattern Recognition
- Some anomalies are only visible at specific time scales
- Daily patterns may be hidden in minute-by-minute data
- Business cycles often operate at hourly, daily, or weekly frequencies

## Files

- **[`freq.yaml`](freq.yaml)**: Anomstack configuration demonstrating frequency parameters

## Configuration Details

The YAML file demonstrates frequency aggregation:
```yaml
metric_batch: 'freq'
# Ingest data frequently (every 5 minutes via cron)
ingest_cron_schedule: "*/5 * * * *"  

# Preprocessing parameters for frequency aggregation
preprocess_params:
  freq: '1H'        # Aggregate to hourly data
  freq_agg: 'mean'  # Use mean aggregation
  diff_n: 1         # Still apply differencing after aggregation
  smooth_n: 3       # Apply smoothing to aggregated data
  lags_n: 5         # Create lag features from aggregated data

# Example SQL that generates high-frequency dummy data
ingest_sql: >
  SELECT
    NOW() as metric_timestamp,
    'high_freq_metric' as metric_name,
    RANDOM() * 100 + 50 * SIN(EXTRACT(epoch FROM NOW()) / 3600) as metric_value
```

### Key Parameters Explained

#### `freq` Parameter
Pandas frequency strings for resampling:
- `'1T'` or `'1min'`: 1 minute
- `'5T'` or `'5min'`: 5 minutes  
- `'1H'`: 1 hour
- `'1D'`: 1 day
- `'1W'`: 1 week
- `'1M'`: 1 month

#### `freq_agg` Parameter
Aggregation methods:
- `'mean'`: Average values (default, good for most metrics)
- `'sum'`: Total values (good for counts, volumes)
- `'max'`: Maximum values (good for peak detection)
- `'min'`: Minimum values (good for baseline monitoring)
- `'std'`: Standard deviation (for volatility measures)

## Setup & Usage

### Prerequisites
- Anomstack environment configured
- Data source that can provide high-frequency metrics
- Understanding of your data's natural frequency patterns

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp metrics/examples/freq/freq.yaml metrics/my_freq_batch.yaml
   ```

2. **Customize frequency settings**: Edit the `preprocess_params`:
   ```yaml
   preprocess_params:
     freq: '4H'        # Aggregate to 4-hour intervals
     freq_agg: 'sum'   # Sum values within each interval
   ```

3. **Adjust ingest frequency**: Match your data collection schedule

4. **Enable in Dagster**: The jobs will process and aggregate automatically

## Common Use Cases & Configurations

### Business Metrics (Minute → Hourly)
```yaml
# Collect sales data every minute, analyze hourly trends
metric_batch: 'sales_hourly'
ingest_cron_schedule: "*/1 * * * *"  # Every minute
preprocess_params:
  freq: '1H'
  freq_agg: 'sum'  # Sum sales within each hour
```

### System Monitoring (Second → Minute)  
```yaml
# Collect system metrics every 10 seconds, detect minute-level anomalies
metric_batch: 'system_minute'
ingest_cron_schedule: "*/10 * * * * *"  # Every 10 seconds
preprocess_params:
  freq: '1T'
  freq_agg: 'mean'  # Average CPU/memory over each minute
```

### IoT Sensor Data (Second → Daily)
```yaml
# Collect sensor readings every second, look for daily patterns
metric_batch: 'sensors_daily'
ingest_cron_schedule: "*/1 * * * * *"  # Every second
preprocess_params:
  freq: '1D'
  freq_agg: 'mean'  # Daily average temperature/pressure
```

### Financial Data (Tick → 5-Minute)
```yaml
# Collect trading data on every tick, analyze 5-minute bars
metric_batch: 'trading_5min'
ingest_cron_schedule: "*/1 * * * * *"  # Every second (tick data)
preprocess_params:
  freq: '5T'
  freq_agg: 'mean'  # 5-minute average prices
```

### Web Analytics (Pageview → Hourly)
```yaml
# Collect pageviews continuously, detect hourly anomalies
metric_batch: 'web_hourly'
ingest_cron_schedule: "*/30 * * * * *"  # Every 30 seconds
preprocess_params:
  freq: '1H'
  freq_agg: 'sum'  # Total pageviews per hour
```

## Advanced Frequency Patterns

### Multi-Level Aggregation
Create multiple metric batches for different time horizons:
```yaml
# Short-term: Minute-level anomalies
metric_batch: 'metrics_1min'
preprocess_params:
  freq: '1T'
  freq_agg: 'mean'

# Medium-term: Hourly anomalies  
metric_batch: 'metrics_1hour'
preprocess_params:
  freq: '1H'
  freq_agg: 'mean'

# Long-term: Daily anomalies
metric_batch: 'metrics_1day'
preprocess_params:
  freq: '1D'
  freq_agg: 'mean'
```

### Mixed Aggregation Methods
```yaml
# Create multiple views of the same data
metric_batch: 'mixed_agg'
ingest_sql: >
  SELECT metric_timestamp, metric_name, metric_value FROM (
    VALUES
      (NOW(), 'revenue_hourly_sum', revenue_value),
      (NOW(), 'revenue_hourly_max', revenue_value),
      (NOW(), 'revenue_hourly_std', revenue_value)
  )
preprocess_params:
  freq: '1H'
  freq_agg: 'mean'  # Will be overridden per metric if needed
```

## Performance Considerations

### Memory Usage
- Higher frequencies = more data points = more memory
- Aggregation reduces memory footprint significantly
- Consider your available RAM when setting frequencies

### Model Training Speed
- More data points = longer training time
- Aggregation can speed up training by 10-100x
- Balance between detail and performance

### Alert Latency
- Higher frequency = faster anomaly detection
- Lower frequency = more stable, less noisy alerts
- Choose based on how quickly you need to respond

## Example Output Transformation

**Before Aggregation** (minute-level data):
```python
[
    {'metric_timestamp': '2024-01-15 10:01:00', 'metric_value': 42.1},
    {'metric_timestamp': '2024-01-15 10:02:00', 'metric_value': 43.5},
    {'metric_timestamp': '2024-01-15 10:03:00', 'metric_value': 41.8},
    # ... 57 more minutes
]
```

**After Aggregation** (hourly data with mean):
```python
[
    {'metric_timestamp': '2024-01-15 10:00:00', 'metric_value': 42.47},  # Average of hour
]
```

## Integration with Anomstack Features

- **Dashboard**: View both raw and aggregated data trends
- **Alerts**: Get notifications based on aggregated anomaly patterns  
- **Change Detection**: Detect changes at the appropriate time scale
- **Model Storage**: Separate models for different frequency levels
- **Preprocessing**: Combines with other preprocessing steps (differencing, smoothing)

This example demonstrates how frequency aggregation can dramatically improve anomaly detection by operating at the right time scale for your data and use case.
