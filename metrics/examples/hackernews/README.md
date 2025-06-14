# HackerNews Anomaly Detection

This **Anomstack metric batch** demonstrates how to use custom Python functions to scrape real-time data from external APIs and detect anomalies in engagement metrics. Never miss a viral story from HackerNews again!

## Overview

This example shows how to:
- Use the `ingest_fn` parameter to define custom Python data ingestion
- Pull live data from the HackerNews API
- Create derived metrics from API responses  
- Detect anomalies in story engagement patterns
- Get alerts when stories go viral or engagement drops

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`hn_top_stories_scores.py`](hn_top_stories_scores.py) to fetch top 10 HackerNews stories
2. **Train Job**: PyOD models learn normal patterns in story scores
3. **Score Job**: Generate anomaly scores for current story metrics
4. **Alert Job**: Send notifications when unusual engagement is detected

### Metrics Generated
- `hn_top_story_score_max`: Highest score among top 10 stories
- `hn_top_story_score_min`: Lowest score among top 10 stories  
- `hn_top_story_score_mean`: Average score of top 10 stories
- `hn_top_story_score_median`: Median score of top 10 stories

## Files

- **[`hn_top_stories_scores.py`](hn_top_stories_scores.py)**: Custom Python ingest function
- **[`hn_top_stories_scores.yaml`](hn_top_stories_scores.yaml)**: Anomstack configuration

## Setup & Usage

### Prerequisites
- No API key required (HackerNews API is free)
- Internet connection for API access
- Anomstack environment set up

### Configuration
The YAML file configures:
```yaml
metric_batch: 'hn_top_stories_scores'
ingest_fn: 'hn_top_stories_scores.py'  # Custom Python function
# Inherits all other settings from defaults
```

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/hackernews metrics/my_hackernews
   ```

2. **Customize if needed**: Modify the Python function to track different metrics

3. **Enable in Dagster**: The jobs will appear in your Dagster UI and run on the configured schedule

### Customization Ideas
- Track specific story types or keywords
- Monitor comment counts and engagement ratios
- Add sentiment analysis of story titles
- Compare against historical viral patterns
- Set up custom alert thresholds for your use case

## API Details

**HackerNews API Endpoints Used**:
- Top Stories: `https://hacker-news.firebaseio.com/v0/topstories.json`
- Story Details: `https://hacker-news.firebaseio.com/v0/item/{id}.json`

**Rate Limits**: HackerNews API is generally rate-limited but quite generous for this use case.

## Example Output

The ingest function returns a pandas DataFrame with:
```python
{
    'metric_timestamp': datetime.now(),
    'metric_name': 'hn_top_story_score_max',
    'metric_value': 486.0
}
```

## Anomaly Detection Scenarios

This example can detect:
- **Viral Stories**: Unusually high max scores indicating trending content
- **Engagement Drops**: Lower than normal average scores
- **Platform Changes**: Sudden shifts in scoring patterns
- **Weekend Effects**: Different engagement patterns by day/time

## Integration with Anomstack Features

- **Dashboard**: View story score trends in the FastHTML dashboard
- **Alerts**: Get Slack/email notifications for unusual HackerNews activity  
- **Change Detection**: Identify shifts in community engagement patterns
- **LLM Alerts**: Use AI to analyze what types of stories are causing anomalies
