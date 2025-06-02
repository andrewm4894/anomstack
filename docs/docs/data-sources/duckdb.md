---
sidebar_position: 5
---

# DuckDB

Anomstack supports DuckDB as a data source for your metrics. DuckDB is a fast analytical database that can read and write data from various file formats.

## Configuration

Configure DuckDB in your metric batch's `config.yaml`:

```yaml
db: "duckdb"
table_key: "metrics"  # Default table to store metrics
metric_batch: "your_metric_batch_name"
ingest_cron_schedule: "*/3 * * * *"  # When to run the ingestion
ingest_sql: >
  select
    current_timestamp() as metric_timestamp,
    'metric_name' as metric_name,
    your_value as metric_value
  from your_table;
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

## Features

DuckDB supports:
- Local file-based databases
- MotherDuck cloud integration
- Reading from various file formats (CSV, Parquet, JSON)
- SQL queries with Python integration

## Examples

Check out the [DuckDB example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/duckdb) for a complete working example.

## Best Practices

- Use appropriate file formats for your data
- Consider query optimization
- Implement proper file permissions
- Use parameterized queries

## Limitations

- Local storage considerations
- Memory usage for large datasets
- Concurrent access limitations

## Related Links

- [DuckDB Documentation](https://duckdb.org/docs)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/duckdb)
- [Default Configuration](https://github.com/andrewm4894/anomstack/tree/main/metrics/defaults/defaults.yaml) 