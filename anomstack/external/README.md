# External Integrations

This directory contains all external platform integrations for Anomstack, allowing you to connect to various data sources and cloud storage solutions.

## Data Sources

Anomstack supports multiple data platforms for querying your metrics:

### Databases
- **BigQuery** (`gcp/bigquery.py`) - Google Cloud BigQuery integration
- **Snowflake** (`snowflake/snowflake.py`) - Snowflake data warehouse integration  
- **ClickHouse** (`clickhouse/clickhouse.py`) - ClickHouse OLAP database integration
- **DuckDB** (`duckdb/duckdb.py`) - DuckDB analytics database integration (also supports MotherDuck)
- **SQLite** (`sqlite/sqlite.py`) - SQLite database integration (also supports Turso)

### Cloud Storage
- **Google Cloud Storage** (`gcp/gcs.py`) - For storing trained models in GCS
- **Amazon S3** (`aws/s3.py`) - For storing trained models in S3 buckets

## Configuration

Each integration requires specific configuration parameters in your environment or metric batch configuration files. Refer to the main README for setup instructions for each platform.

## Usage

These integrations are automatically used based on your metric batch configuration. You specify the data source type in your `.yaml` configuration files, and Anomstack will use the appropriate integration to:

1. Ingest metrics data from your chosen platform
2. Store trained ML models in your chosen storage backend
3. Query historical data for anomaly detection

## Adding New Integrations

To add support for a new data platform:

1. Create a new subdirectory for the platform
2. Implement the required interface methods for data ingestion
3. Add configuration support in the main config system
4. Update the main README with the new integration

See existing integrations as reference implementations.
