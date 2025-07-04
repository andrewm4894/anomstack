# Anomstack Metric Batch Examples

This directory contains example **metric batches** that demonstrate various ways to configure and use Anomstack for anomaly detection on different data sources and use cases. Each example shows how to define metrics using either SQL queries or custom Python functions within the Anomstack/Dagster pipeline.

## What is a Metric Batch?

A **metric batch** is Anomstack's core concept - a collection of related metrics that go through the same pipeline of Dagster jobs:
1. **Ingest**: Pull data using SQL or Python
2. **Train**: Train PyOD models on historical data  
3. **Score**: Generate anomaly scores
4. **Alert**: Send notifications when anomalies are detected

## Example Categories

### 🗄️ Database Sources
- **[bigquery](bigquery/)**: BigQuery metric batches with SQL queries
- **[snowflake](snowflake/)**: Snowflake integration examples
- **[s3](s3/)**: S3-based data source examples

### 🌐 API Integrations  
- **[hackernews](hackernews/)**: Scrape HackerNews top stories using custom Python
- **[weather](weather/)**: OpenMeteo weather data via Python API calls
- **[weather_forecast](weather_forecast/)**: Weather forecast data from Snowflake
- **[yfinance](yfinance/)**: Yahoo Finance stock data via Python
- **[coindesk](coindesk/)**: Cryptocurrency data from CoinDesk API
- **[gtrends](gtrends/)**: Google Trends data from BigQuery
- **[prometheus](prometheus/)**: Prometheus metrics ingestion
- **[netdata](netdata/)**: Netdata monitoring system integration
- **[netdata_httpcheck](netdata_httpcheck/)**: Website availability monitoring
- **[tomtom](tomtom/)**: TomTom traffic API integration
- **[github](github/)**: GitHub API metrics (stars, issues, etc.)
- **[posthog](posthog/)**: PostHog query API usage metrics
- **[currency](currency/)**: Currency exchange rate monitoring
- **[eirgrid](eirgrid/)**: Irish electrical grid data

### 📝 Configuration Patterns
- **[example_simple](example_simple/)**: Minimal YAML-only configuration
- **[example_sql_file](example_sql_file/)**: Using separate SQL files
- **[example_jinja](example_jinja/)**: Jinja templating in configurations
- **[freq](freq/)**: Frequency aggregation and resampling
- **[python](python/)**: Custom Python ingest functions
- **[sales](sales/)**: Business metrics from SQL
- **[users](users/)**: User analytics metrics

### 🏗️ Infrastructure Examples
- **[gsod](gsod/)**: Global weather data from public BigQuery datasets

## Quick Start

1. **Choose an example** that matches your data source or use case
2. **Copy the configuration** - each example has a `.yaml` file with settings
3. **Customize the data source** - modify SQL queries or Python functions
4. **Set environment variables** - configure database connections, API keys, etc.
5. **Run in Dagster** - the jobs will automatically ingest, train, score, and alert

## File Structure

Each example typically contains:
```
example_name/
├── README.md              # Documentation and setup instructions
├── example_name.yaml      # Anomstack configuration
├── example_name.sql       # SQL query (for SQL-based examples)
└── example_name.py        # Python function (for Python-based examples)
```

## Configuration Inheritance

All examples inherit default settings from [`../defaults/defaults.yaml`](../defaults/defaults.yaml). You only need to specify:
- Data source connection details
- Custom SQL queries or Python functions  
- Any parameter overrides specific to your use case

## Environment Setup

Most examples require environment variables for:
- **Database connections**: `DB_CONNECTION_STRING`, `GCP_PROJECT_ID`, etc.
- **API keys**: `OPENMETEO_API_KEY`, `SLACK_WEBHOOK_URL`, etc.
- **Alert configuration**: `EMAIL_SMTP_SERVER`, `ALERT_EMAIL_TO`, etc.

See [`.example.env`](../../.example.env) for a complete list of available environment variables.

## Next Steps

1. **Explore the examples** to understand different patterns
2. **Create your own metric batch** by copying and modifying an example
3. **Check the [main documentation](../../README.md)** for deployment options
4. **Visit the [defaults documentation](../defaults/README.md)** to understand configuration options

---

## Complete Example List

- [bigquery](bigquery/): Example of a BigQuery metric batch.
- [coindesk](coindesk/): Example of a CoinDesk metric batch.
- [eirgrid](eirgrid/): Example of a metric batch that uses a custom python `ingest_fn` parameter to just use python to create an `ingest()` function that returns a pandas df.
- [example_jinja](example_jinja/): Example of a metric batch that uses Jinja templating.
- [example_simple](example_simple/): Example of a simple metric batch.
- [example_sql_file](example_sql_file/): Example of a metric batch that uses a SQL file.
- [freq](freq/): Example of a metric batch that uses the `freq` parameter.
- [gsod](gsod/): Example of a metric batch that uses GSOD data from BigQuery.
- [gtrends](gtrends/): Example of a metric batch that uses Google Trends data from BigQuery.
- [hackernews](hackernews/): Example of a metric batch that uses the Hacker News API.
- [netdata](netdata/): Example of a metric batch that uses the Netdata API.
- [netdata_httpcheck](netdata_httpcheck/): Example of a metric batch that uses the Netdata API to check the status of a website.
- [prometheus](prometheus/): Example of a metric batch that uses Prometheus.
- [python](python/): Example of a metric batch that uses a custom python `ingest_fn` parameter to just use python to create an `ingest()` function that returns a pandas df.
- [s3](s3/): Example of a metric batch that uses S3.
- [sales](sales/): Example of a metric batch that uses a SQL file.
- [snowflake](snowflake/): Example of a metric batch that uses Snowflake.
- [tomtom](tomtom/): Example of a metric batch that uses the TomTom API.
- [users](users/): Example of a metric batch that uses a SQL file.
- [weather](weather/): Example of a metric batch that uses Open Meteo data.
- [weather_forecast](weather_forecast/): Example of a metric batch that uses weather forecast data from Snowflake.
- [yfinance](yfinance/): Example of a metric batch that uses the Yahoo Finance API.
