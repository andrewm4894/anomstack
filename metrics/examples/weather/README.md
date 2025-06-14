# Weather Anomaly Detection

This **Anomstack metric batch** demonstrates how to ingest real-time weather data from external APIs and detect anomalies in temperature patterns. Perfect for monitoring climate variations, detecting extreme weather events, or tracking seasonal patterns.

## Overview

This example shows how to:
- Use custom Python functions with the `ingest_fn` parameter
- Pull live weather data from the [Open Meteo API](https://open-meteo.com/)
- Monitor multiple cities simultaneously
- Detect unusual temperature patterns and weather anomalies
- Set up alerts for extreme weather conditions

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`ingest_weather.py`](ingest_weather.py) to fetch current temperature data
2. **Train Job**: PyOD models learn normal temperature patterns for each city
3. **Score Job**: Generate anomaly scores for current temperature readings
4. **Alert Job**: Send notifications when unusual temperature patterns are detected

### Data Source
**Open Meteo API**: Free weather API providing current and forecast weather data
- **Example API Call**: [`https://api.open-meteo.com/v1/forecast?latitude=53.3441&longitude=-6.2675&current=temperature_2m`](https://api.open-meteo.com/v1/forecast?latitude=53.3441&longitude=-6.2675&current=temperature_2m)
- **Rate Limits**: 10,000 requests per day (generous for monitoring use cases)
- **No API Key Required**: Open and free to use

## Files

- **[`ingest_weather.py`](ingest_weather.py)**: Custom Python ingest function
- **[`weather.yaml`](weather.yaml)**: Anomstack configuration

## Setup & Usage

### Prerequisites
- Internet connection for API access
- Anomstack environment configured
- No API key required (Open Meteo is free)

### Configuration
The YAML file configures:
```yaml
metric_batch: 'weather'
ingest_fn: 'ingest_weather.py'  # Custom Python function
# Optional: Override default alert thresholds for weather monitoring
alert_threshold: 0.7  # Lower threshold for more sensitive weather alerts
```

### Default Cities Monitored
The example monitors these cities by default:
- **Dublin, Ireland** (53.3441, -6.2675)
- **London, UK** (51.5074, -0.1278)  
- **New York, USA** (40.7128, -74.0060)
- **Tokyo, Japan** (35.6762, 139.6503)

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/weather metrics/my_weather
   ```

2. **Customize cities**: Edit `ingest_weather.py` to add your locations:
   ```python
   cities = [
       {"name": "your_city", "lat": 40.7128, "lon": -74.0060},
       # Add more cities here
   ]
   ```

3. **Enable in Dagster**: The jobs will appear in your Dagster UI and run on schedule

### Customization Ideas
- **Add more weather parameters**: humidity, wind speed, pressure, precipitation
- **Historical comparisons**: Compare current temps to historical averages
- **Regional monitoring**: Focus on specific geographical areas
- **Seasonal adjustments**: Account for expected seasonal variations
- **Extreme weather alerts**: Set custom thresholds for heat waves, cold snaps

## Example Output

The ingest function returns temperature data for each city:
```python
[
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'temperature_dublin',
        'metric_value': 12.5
    },
    {
        'metric_timestamp': datetime.now(), 
        'metric_name': 'temperature_london',
        'metric_value': 15.2
    }
]
```

## Anomaly Detection Scenarios

This example can detect:
- **Heat Waves**: Unusually high temperatures for the season
- **Cold Snaps**: Sudden temperature drops below normal ranges
- **Climate Shifts**: Long-term changes in temperature patterns
- **Seasonal Anomalies**: Temperatures out of sync with expected seasonal patterns
- **Urban Heat Islands**: Temperature variations within metropolitan areas

## Integration with Anomstack Features

- **Dashboard**: Visualize temperature trends across cities in the FastHTML dashboard
- **Alerts**: Get Slack/email notifications for extreme weather events
- **Change Detection**: Identify shifts in local climate patterns
- **LLM Alerts**: Use AI to analyze and explain unusual weather patterns
- **Frequency Settings**: Monitor at different intervals (hourly, daily, etc.)

## Environment Variables

Optional environment variables for customization:
```bash
# Custom alert settings for weather monitoring
WEATHER_ALERT_THRESHOLD=0.7
WEATHER_CITIES="dublin,london,newyork,tokyo"  # Comma-separated list
```

## API Integration Details

**Open Meteo API Parameters Used**:
- `latitude` / `longitude`: City coordinates
- `current=temperature_2m`: Current temperature in Celsius
- `timezone=auto`: Automatic timezone detection

**Response Format**:
```json
{
  "current": {
    "time": "2024-01-15T10:00",
    "temperature_2m": 12.5
  }
}
```
