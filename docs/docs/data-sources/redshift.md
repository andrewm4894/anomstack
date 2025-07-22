---
sidebar_position: 9
---

# Redshift

Anomstack supports Amazon Redshift as a data source for your metrics. Redshift is a fully managed, petabyte-scale data warehouse service.

## Configuration

Configure Redshift in your metric batch's `config.yaml`:

```yaml
db: "redshift"
table_key: "your_database.schema.metrics"  # Your Redshift database, schema, and table
metric_batch: "your_metric_batch_name"
ingest_cron_schedule: "*/3 * * * *"  # When to run the ingestion
ingest_sql: >
  select
    current_timestamp as metric_timestamp,
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

Redshift provides:
- Petabyte-scale data warehouse
- Columnar storage
- Parallel query execution
- Advanced analytics

## Examples

Check out the [Redshift example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/redshift) for a complete working example.

## Best Practices

- Query optimization
- Distribution key selection
- Sort key optimization
- Workload management
- Cost optimization

## Limitations

- Query timeout limits
- Concurrent query limits
- Storage limitations
- Cost considerations

## Related Links

- [Redshift Documentation](https://docs.aws.amazon.com/redshift/)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/redshift)
- [Default Configuration](https://github.com/andrewm4894/anomstack/tree/main/metrics/defaults/defaults.yaml)
