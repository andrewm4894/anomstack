---
sidebar_position: 2
---

# Quickstart Guide

This guide will help you get started with Anomstack quickly. We'll cover the basic setup and show you how to monitor your first metric.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/andrewm4894/anomstack.git
cd anomstack
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Basic Configuration

1. Create a new metric batch in the `metrics` directory:
```bash
mkdir -p metrics/my_first_metric
```

2. Create a SQL file for your metric (`metrics/my_first_metric/query.sql`):
```sql
SELECT 
    timestamp,
    value
FROM your_table
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY timestamp
```

3. Create a configuration file (`metrics/my_first_metric/config.yaml`):
```yaml
name: my_first_metric
description: "My first metric in Anomstack"
source:
    type: sqlite  # or your preferred data source
    query: query.sql
schedule: "0 * * * *"  # Run every hour
```

## Running Anomstack

1. Start the Dagster UI:
```bash
dagster dev -f anomstack/main.py
```

2. Start the dashboard:
```bash
python dashboard/app.py
```

3. Access the dashboard at `http://localhost:5000`

## Monitoring Your Metric

1. The metric will be automatically ingested based on your schedule
2. Anomstack will train a model on your historical data
3. New data points will be scored for anomalies
4. You'll receive alerts if anomalies are detected

## Next Steps

- [Learn about concepts](concepts)
- [Configure alerts](features/alerts)
- [Customize the dashboard](features/dashboard)
- [Explore deployment options](deployment/docker)

## Ready-Made Example Metrics

Want to see Anomstack in action with real data? Try these ready-made example metric batches:

- [Currency](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/currency): Track currency exchange rates from public APIs.
- [Yahoo Finance (yfinance)](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/yfinance): Monitor stock prices and financial data using the Yahoo Finance API.
- [Weather](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/weather): Analyze weather data from Open Meteo.
- [CoinDesk](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/coindesk): Get Bitcoin price data from the CoinDesk API.
- [Hacker News](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/hackernews): Track top stories and scores from Hacker News.
- [Netdata](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/netdata): Monitor system metrics using the Netdata API.

See the [full list of examples](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples) for more, including BigQuery, Prometheus, Google Trends, and more.

## Common Issues

### Metric Not Showing Up
- Check the Dagster UI for any job failures
- Verify your SQL query returns the expected data
- Ensure your configuration file is valid YAML

### No Alerts
- Check your alert configuration
- Verify your email/Slack settings
- Look for any alert throttling settings

## Need Help?

- Check the [GitHub Issues](https://github.com/andrewm4894/anomstack/issues)
- Join our [Discord Community](https://discord.gg/anomstack)
- Read the [detailed documentation](intro) 