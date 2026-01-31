---
sidebar_position: 5
---

# LLM Agent

The LLM (Large Language Model) agent in Anomstack provides AI-powered anomaly detection using the [anomaly-agent](https://github.com/andrewm4894/anomaly-agent) library. It analyzes time series data using multimodal LLMs to identify anomalies with natural language explanations.

## Features

- **LLM-Powered Detection**: Uses OpenAI models (gpt-5-mini by default) for intelligent anomaly identification
- **Multimodal Analysis**: Optionally includes time series plots for visual pattern recognition
- **Two-Stage Pipeline**: Detection and verification phases to reduce false positives
- **Natural Language Explanations**: Get human-readable descriptions of detected anomalies
- **PostHog Integration**: Automatic LLM analytics tracking when PostHog is configured

## Configuration

Configure the LLM agent in your metric batch YAML or `defaults.yaml`:

```yaml
# Enable LLM alerts for a metric batch
disable_llmalert: False
llmalert_default_schedule_status: 'RUNNING'

# LLM alert parameters
llmalert_model: "gpt-5-mini"                  # OpenAI model to use for LLM alerts
llmalert_recent_n: 5                          # Number of recent observations to analyze
llmalert_smooth_n: 0                          # Smoothing applied before analysis
llmalert_metric_rounding: -1                  # Decimal places for rounding (-1 = no rounding)
llmalert_metric_timestamp_max_days_ago: 30    # Max age of metrics to analyze
llmalert_prompt_max_n: 1000                   # Max observations in prompt
llmalert_include_plot: True                   # Include visual plot for multimodal analysis
llmalert_cron_schedule: "*/5 * * * *"         # How often to run LLM analysis
```

### Multimodal Image Support

When `llmalert_include_plot: True` (default), Anomstack generates a matplotlib visualization of the time series and sends it alongside the numeric data to the LLM. This enables:

- Visual pattern recognition for trends, seasonality, and outliers
- More context-aware anomaly descriptions
- Better detection of patterns that may not be obvious in raw numbers

The plot is encoded as base64 PNG and works with any multimodal-capable model (gpt-5-mini, gpt-4o-mini, gpt-4o, etc.).

### Custom Prompts

You can customize the detection and verification prompts:

```yaml
llmalert_anomaly_agent_detection_prompt: |
  You are an expert anomaly detection agent analyzing server metrics.
  Focus on: CPU spikes, memory leaks, unusual network patterns.
  Consider time of day and typical usage patterns.

llmalert_anomaly_agent_verification_prompt: |
  You are an expert anomaly verification agent.
  Review detected anomalies and confirm only those that represent genuine issues.
  Consider normal business operations and seasonality.
```

## Environment Variables

Required environment variables for LLM alerts:

```bash
# Required: OpenAI API key
OPENAI_API_KEY=your-openai-api-key

# Optional: PostHog for LLM analytics tracking
POSTHOG_API_KEY=your-posthog-api-key
POSTHOG_ENABLED=true
```

You can override llmalert settings per metric batch using the standard override pattern:

```bash
ANOMSTACK__MY_BATCH__LLMALERT_MODEL=gpt-4o
ANOMSTACK__MY_BATCH__LLMALERT_INCLUDE_PLOT=True
ANOMSTACK__MY_BATCH__DISABLE_LLMALERT=False
```

## How It Works

1. **Data Collection**: The `llmalert_sql` query retrieves recent metric data
2. **Plot Generation**: If `llmalert_include_plot=True`, a matplotlib plot is created
3. **LLM Analysis**: Data (and optionally the plot) is sent to the anomaly-agent
4. **Detection**: The LLM identifies potential anomalies with descriptions
5. **Verification** (optional): A second LLM pass filters false positives
6. **Output**: Anomalies are logged and can trigger alerts

## Integration with PostHog

When PostHog is configured, LLM calls are automatically tracked in PostHog's LLM Analytics:

- Token usage and costs
- Input/output content (including images when multimodal)
- Latency metrics
- Model information

This provides visibility into LLM usage across your anomaly detection pipeline.

## Example Output

When an anomaly is detected, you'll see output like:

```
Detected anomaly in metric 'cpu_usage':
  Timestamp: 2024-01-15 14:30:00
  Value: 98.5
  Description: Significant CPU spike to 98.5%, well above the normal
  range of 20-40%. This appears to be a genuine anomaly that warrants
  investigation, possibly indicating a runaway process or resource
  exhaustion.
```

## Best Practices

1. **Start with defaults**: The default settings work well for most use cases
2. **Enable multimodal**: Keep `llmalert_include_plot: True` for better detection
3. **Tune `llmalert_recent_n`**: Adjust based on your metric frequency
4. **Custom prompts**: Use domain-specific prompts for specialized metrics
5. **Monitor costs**: Use PostHog to track LLM token usage and costs

## Troubleshooting

### LLM alerts not running
- Check `disable_llmalert: False` in your config
- Verify `llmalert_default_schedule_status: 'RUNNING'`
- Ensure `OPENAI_API_KEY` is set

### No anomalies detected
- The LLM may not find anomalies if data is normal
- Check `llmalert_recent_n` includes enough data points
- Review the data being sent with debug logging

### High token usage
- Reduce `llmalert_prompt_max_n` to limit data sent
- Adjust `llmalert_cron_schedule` to run less frequently
- Consider disabling verification for cost savings
