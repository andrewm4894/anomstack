---
sidebar_position: 4
---

# ClickHouse

Anomstack supports ClickHouse as a data source for your metrics.

## Configuration

Configure ClickHouse in your metric batch's `config.yaml`:

```yaml
db: "clickhouse"
table_key: "your_database.your_table"
metric_batch: "your_metric_batch_name"
ingest_cron_schedule: "*/10 * * * *"  # When to run the ingestion
ingest_sql: >
  select
    now() as metric_timestamp,
    'metric_name' as metric_name,
    your_value as metric_value
  from your_table;
```

## Authentication

You can authenticate with ClickHouse using:
- Username and password
- Environment variables
- SSL/TLS certificates

## Examples

Check out the [ClickHouse example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/clickhouse) for a complete working example.

## Best Practices

- Use appropriate table engines
- Consider query optimization
- Implement proper access controls
- Use parameterized queries

## Limitations

- Memory usage considerations
- Query timeout limits
- Concurrent query limits

## Related Links

- [ClickHouse Documentation](https://clickhouse.com/docs)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/clickhouse) 