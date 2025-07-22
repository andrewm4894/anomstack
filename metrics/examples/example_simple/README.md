# Simple Metric Batch Example

This **Anomstack metric batch** demonstrates the most basic configuration pattern - a minimal YAML-only setup perfect for getting started with anomaly detection. This example shows how to monitor random dummy metrics without requiring external APIs, databases, or complex setup.

## Overview

This example shows how to:
- Use the simplest possible Anomstack configuration
- Define metrics directly in YAML using inline SQL
- Monitor synthetic data for learning purposes
- Understand the minimal requirements for a metric batch
- Use as a template for your own metric batches

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Executes the inline SQL to generate random dummy metrics
2. **Train Job**: PyOD models learn patterns in the synthetic data
3. **Score Job**: Generate anomaly scores for the dummy metrics
4. **Alert Job**: Send notifications when anomalies are detected (useful for testing)

### What Makes It "Simple"
- **No external dependencies**: Uses only built-in SQL functions
- **No API keys required**: Everything runs locally
- **Minimal configuration**: Only essential parameters specified
- **Self-contained**: Perfect for testing and learning

## Files

- **[`example_simple.yaml`](example_simple.yaml)**: Complete Anomstack configuration

## Configuration Details

The YAML file demonstrates:
```yaml
metric_batch: 'example_simple'
# Uses default ingest_sql with inline query
ingest_sql: >
  SELECT
    NOW() as metric_timestamp,
    'dummy_metric_' || CAST(FLOOR(RANDOM() * 3) AS VARCHAR) as metric_name,
    RANDOM() * 100 as metric_value
# All other settings inherited from defaults
```

Key aspects:
- **Inline SQL**: Query defined directly in YAML (no separate .sql file)
- **Synthetic Data**: Generates random metrics for demonstration
- **Default Inheritance**: Uses all default settings from [`../defaults/defaults.yaml`](../defaults/defaults.yaml)
- **Multiple Metrics**: Creates 3 different dummy metrics (`dummy_metric_0`, `dummy_metric_1`, `dummy_metric_2`)

## Setup & Usage

### Prerequisites
- Anomstack environment set up
- Default database configured (DuckDB works great for this example)
- No external dependencies required

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp metrics/examples/example_simple/example_simple.yaml metrics/my_simple_batch.yaml
   ```

2. **Customize the metrics**: Edit the SQL to generate your desired test data:
   ```sql
   SELECT
     NOW() as metric_timestamp,
     'my_test_metric' as metric_name,
     RANDOM() * 50 + 25 as metric_value  -- Random values between 25-75
   ```

3. **Enable in Dagster**: The jobs will appear in your Dagster UI

### Customization Examples

**Monitor a single metric**:
```sql
SELECT
  NOW() as metric_timestamp,
  'single_metric' as metric_name,
  RANDOM() * 100 as metric_value
```

**Create time-based patterns**:
```sql
SELECT
  NOW() as metric_timestamp,
  'time_based_metric' as metric_name,
  50 + 20 * SIN(EXTRACT(hour FROM NOW()) * 2 * PI() / 24) as metric_value
```

**Simulate business metrics**:
```sql
SELECT
  NOW() as metric_timestamp,
  metric_name,
  metric_value
FROM VALUES
  ('daily_revenue', RANDOM() * 10000 + 5000),
  ('user_signups', RANDOM() * 100 + 50),
  ('page_views', RANDOM() * 50000 + 25000)
```

## Learning Opportunities

This example is perfect for:
- **Understanding Anomstack basics**: See how metric batches work
- **Testing configurations**: Experiment with different settings safely
- **Learning SQL patterns**: Practice writing ingest queries
- **Anomaly detection concepts**: Observe how PyOD models work with different data patterns
- **Alert testing**: Verify your notification setup works

## Example Output

The ingest generates data like:
```python
[
    {
        'metric_timestamp': '2024-01-15 10:00:00',
        'metric_name': 'dummy_metric_0',
        'metric_value': 42.7
    },
    {
        'metric_timestamp': '2024-01-15 10:00:00',
        'metric_name': 'dummy_metric_1',
        'metric_value': 78.1
    }
]
```

## Next Steps

Once you're comfortable with this example:
1. **Try other examples**: Explore API-based examples like [weather](../weather/) or [hackernews](../hackernews/)
2. **Connect real data**: Replace the dummy SQL with queries to your actual databases
3. **Customize alerts**: Override default thresholds and notification settings
4. **Add complexity**: Combine multiple data sources into a single metric batch

## Integration with Anomstack Features

- **Dashboard**: View the dummy metrics in the FastHTML dashboard
- **Alerts**: Test your email/Slack notification setup
- **Change Detection**: Experiment with change detection algorithms
- **Model Training**: Observe how different PyOD models perform on synthetic data
