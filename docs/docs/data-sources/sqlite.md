---
sidebar_position: 6
---

# SQLite

Anomstack supports SQLite as a data source for your metrics. SQLite is a lightweight, file-based database that's perfect for local development and small to medium-sized applications.

## Configuration

Configure SQLite in your metric batch's `config.yaml`:

```yaml
db: "sqlite"
table_key: "metrics"  # Default table to store metrics
metric_batch: "your_metric_batch_name"
ingest_cron_schedule: "*/3 * * * *"  # When to run the ingestion
ingest_sql: >
  select
    datetime('now') as metric_timestamp,
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

SQLite provides:
- File-based database storage
- Zero configuration
- ACID compliance
- Full SQL support

## Examples

Check out the [SQLite example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/sqlite) for a complete working example.

## Best Practices

- Regular database backups
- Proper file permissions
- Index optimization
- Query optimization

## Limitations

- Concurrent write operations
- File size limitations
- Memory constraints
- Network access limitations

## Related Links

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/sqlite)
- [Default Configuration](https://github.com/andrewm4894/anomstack/tree/main/metrics/defaults/defaults.yaml) 