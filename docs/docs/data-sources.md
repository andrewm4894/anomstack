---
sidebar_position: 4
---

# Data Sources

Anomstack supports multiple data sources for ingesting metrics. Choose the data source that matches your infrastructure:

## Supported Data Sources

### 🐍 Programming Languages
- **[Python](data-sources/python)** - Direct Python functions for custom data ingestion

### ☁️ Cloud Data Warehouses  
- **[BigQuery](data-sources/bigquery)** - Google Cloud's serverless data warehouse
- **[Snowflake](data-sources/snowflake)** - Cloud-native data platform
- **[Redshift](data-sources/redshift)** - Amazon's data warehouse service

### 🗄️ Databases
- **[DuckDB](data-sources/duckdb)** - Embedded analytical database  
- **[MotherDuck](data-sources/motherduck)** - Serverless DuckDB in the cloud
- **[SQLite](data-sources/sqlite)** - Lightweight file-based database
- **[ClickHouse](data-sources/clickhouse)** - Columnar database for analytics
- **[Turso](data-sources/turso)** - SQLite for the edge

## Getting Started

1. **Choose your data source** from the list above
2. **Follow the setup guide** for your specific data source
3. **Configure connection details** in your environment variables
4. **Create metric configurations** that query your data
5. **Run your first anomaly detection job**

## Universal Concepts

All data sources work with the same core concepts:

- **SQL queries** to extract time-series metrics
- **Environment variables** for connection configuration  
- **Metric batches** to organize related metrics
- **Schedules** to run data ingestion automatically

## Need Help?

- Check the [environment variables guide](configuration/environment-variables) for connection setup
- Review metric configuration examples in the [metrics directory](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples)
- Join our [GitHub Discussions](https://github.com/andrewm4894/anomstack/discussions) for community support
