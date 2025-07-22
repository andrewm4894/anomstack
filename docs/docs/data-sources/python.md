---
sidebar_position: 1
---

# Python

Anomstack supports Python as a data source for your metrics. This allows you to create custom data ingestion logic using Python's rich ecosystem of libraries.

## Configuration

Configure Python in your metric batch's `config.yaml`:

```yaml
metric_batch: "your_metric_batch_name"
table_key: "your_table_key"
ingest_cron_schedule: "45 6 * * *"  # When to run the ingestion
ingest_fn: >
  {% include "./path/to/your/python/file.py" %}
```

## Default Configuration

Many configuration parameters can be set in `metrics/defaults/defaults.yaml` to apply across all metric batches. Key defaults include:

```yaml
db: "duckdb"  # Default database type
table_key: "metrics"  # Default table name
ingest_cron_schedule: "*/3 * * * *"  # Default ingestion schedule
model_path: "local://./models"  # Default model storage location
alert_methods: "email,slack"  # Default alert methods
```

You can override any of these defaults in your metric batch's configuration file.

## Customizing Default Templates

Anomstack uses several default templates for preprocessing, SQL queries, and other operations. You can customize these by modifying the files in:

1. **Python Templates** (`metrics/defaults/python/`):
   - `preprocess.py`: Customize how metrics are preprocessed before anomaly detection
   - Add your own Python functions for custom processing

2. **SQL Templates** (`metrics/defaults/sql/`):
   - `train.sql`: SQL for training data preparation
   - `score.sql`: SQL for scoring data preparation
   - `alerts.sql`: SQL for alert generation
   - `change.sql`: SQL for change detection
   - `plot.sql`: SQL for metric visualization
   - `llmalert.sql`: SQL for LLM-based alerts
   - `dashboard.sql`: SQL for dashboard data
   - `delete.sql`: SQL for data cleanup
   - `summary.sql`: SQL for summary reports

To use custom templates, modify the corresponding files in these directories. The changes will apply to all metric batches unless overridden in specific batch configurations.

## Example: HackerNews Top Stories

Here's a complete example that fetches metrics from HackerNews top stories:

```python
import pandas as pd
import requests

def ingest(top_n=10) -> pd.DataFrame:
    # Hacker News API endpoint for top stories
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"

    # Get top story IDs
    response = requests.get(url)
    story_ids = response.json()[:top_n]

    # Calculate metrics
    min_score = float("inf")
    max_score = 0
    total_score = 0

    for story_id in story_ids:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()
        score = story.get("score", 0)

        min_score = min(min_score, score)
        max_score = max(max_score, score)
        total_score += score

    avg_score = total_score / len(story_ids)

    # Create DataFrame with metrics
    data = [
        [f"hn_top_{top_n}_min_score", min_score],
        [f"hn_top_{top_n}_max_score", max_score],
        [f"hn_top_{top_n}_avg_score", avg_score],
        [f"hn_top_{top_n}_total_score", total_score],
    ]
    df = pd.DataFrame(data, columns=["metric_name", "metric_value"])
    df["metric_timestamp"] = pd.Timestamp.utcnow()

    return df
```

### How It Works

1. **Configuration**:
   ```yaml
   metric_batch: "hn_top_stories_scores"
   table_key: "metrics_hackernews"
   ingest_cron_schedule: "45 6 * * *"
   ingest_fn: >
     {% include "./examples/hackernews/hn_top_stories_scores.py" %}
   ```

2. **Function Definition**: The `ingest()` function takes a `top_n` parameter to specify how many top stories to analyze.

3. **Data Collection**:
   - Fetches top story IDs from HackerNews API
   - Retrieves details for each story
   - Calculates min, max, average, and total scores

4. **DataFrame Creation**:
   - Creates a DataFrame with required columns: `metric_name`, `metric_value`, and `metric_timestamp`
   - Each metric is a separate row in the DataFrame
   - Timestamps are in UTC

## Best Practices

- Return a pandas DataFrame with required columns
- Include proper error handling
- Use type hints for better code clarity
- Document your functions
- Handle API rate limits and timeouts
- Use environment variables for sensitive data

## Required DataFrame Structure

Your Python function must return a pandas DataFrame with these columns:
- `metric_name`: String identifier for the metric
- `metric_value`: Numeric value of the metric
- `metric_timestamp`: UTC timestamp of when the metric was collected

## Limitations

- Python environment must have required dependencies installed
- Function execution time limits
- Memory usage considerations
- API rate limits for external services

## Related Links

- [Example Implementation](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/hackernews)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Best Practices](https://docs.python-guide.org/)
- [Default Configuration](https://github.com/andrewm4894/anomstack/tree/main/metrics/defaults/defaults.yaml)
- [Default Templates](https://github.com/andrewm4894/anomstack/tree/main/metrics/defaults)
