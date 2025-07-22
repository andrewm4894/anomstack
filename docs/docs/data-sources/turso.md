---
sidebar_position: 8
---

# Turso

Anomstack supports Turso as a data source for your metrics. Turso is a distributed SQLite database that provides global replication and edge computing capabilities.

## Configuration

Configure Turso in your metric batch's `config.yaml`:

```yaml
db: "turso"
table_key: "your_database.metrics"  # Your Turso database and table
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

Turso provides:
- Global replication
- Edge computing
- SQLite compatibility
- Real-time sync

## Examples

Check out the [Turso example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/turso) for a complete working example.

## Best Practices

- Token security
- Query optimization
- Replication strategy
- Data partitioning

## Limitations

- Query timeout limits
- Concurrent query limits
- Storage limitations
- Cost considerations

## Related Links

- [Turso Documentation](https://turso.tech/docs)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/turso)
- [Default Configuration](https://github.com/andrewm4894/anomstack/tree/main/metrics/defaults/defaults.yaml)
