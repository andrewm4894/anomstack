---
sidebar_position: 7
---

# MotherDuck

Anomstack supports MotherDuck as a data source for your metrics. MotherDuck is a cloud-based version of DuckDB that provides serverless analytics capabilities.

## Configuration

Configure MotherDuck in your metric batch's `config.yaml`:

```yaml
db: "motherduck"
table_key: "your_database.metrics"  # Your MotherDuck database and table
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

MotherDuck provides:
- Serverless analytics
- Cloud storage integration
- Real-time collaboration
- DuckDB compatibility

## Examples

Check out the [MotherDuck example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/motherduck) for a complete working example.

## Best Practices

- Token security
- Query optimization
- Cost management
- Data partitioning

## Limitations

- Query timeout limits
- Concurrent query limits
- Storage limitations
- Cost considerations

## Related Links

- [MotherDuck Documentation](https://motherduck.com/docs)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/motherduck)
- [Default Configuration](https://github.com/andrewm4894/anomstack/tree/main/metrics/defaults/defaults.yaml)
