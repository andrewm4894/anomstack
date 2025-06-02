---
sidebar_position: 2
---

# BigQuery

Anomstack supports Google BigQuery as a data source for your metrics.

## Configuration

Configure BigQuery in your metric batch's `config.yaml`:

```yaml
db: "bigquery"
table_key: "your-project.dataset.table"
metric_batch: "your_metric_batch_name"
ingest_cron_schedule: "*/10 * * * *"  # When to run the ingestion
ingest_sql: >
  select
    current_timestamp() as metric_timestamp,
    'metric_name' as metric_name,
    your_value as metric_value
  from your_table;
```

## Authentication

You can authenticate with BigQuery in several ways:
- Service account credentials file
- Application Default Credentials
- Environment variables

## Examples

Check out the [BigQuery example](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/bigquery) for a complete working example.

## Best Practices

- Use parameterized queries for better security
- Consider query costs and optimization
- Use appropriate table partitioning
- Set up proper IAM permissions

## Limitations

- Query execution time limits
- Cost considerations for large queries
- Rate limits and quotas

## Related Links

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Example Queries](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/bigquery) 