---
sidebar_position: 3
---

# Snowflake

Anomstack supports Snowflake as a data source for your metrics.

## Configuration

Configure Snowflake in your metric batch's `config.yaml`:

```yaml
db: "snowflake"
table_key: "YOUR_DATABASE.SCHEMA.TABLE"
metric_batch: "your_metric_batch_name"
ingest_cron_schedule: "*/60 * * * *"  # When to run the ingestion
ingest_sql: >
  select
    current_timestamp() as metric_timestamp,
    'metric_name' as metric_name,
    your_value as metric_value
  from your_table;
```

## Authentication

You can authenticate with Snowflake using:
- Username and password
- Key pair authentication
- OAuth
- Environment variables

## Examples

Check out the [Snowflake example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/snowflake) for a complete working example.

## Best Practices

- Use appropriate warehouse sizing
- Consider query optimization
- Implement proper access controls
- Use parameterized queries

## Limitations

- Warehouse credits consumption
- Query timeout limits
- Concurrent query limits

## Related Links

- [Snowflake Documentation](https://docs.snowflake.com/)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/snowflake) 