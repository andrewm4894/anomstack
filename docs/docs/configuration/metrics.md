---
sidebar_position: 1
---

# Metrics Configuration

Learn how to configure metrics in Anomstack.

## Configuration File

The `config.yaml` file defines:
- Metric properties
- Data source settings
- Schedule configuration
- Alert thresholds
- Custom parameters

## Overriding Config with Environment Variables

You can override any configuration parameter for a specific metric batch using environment variables of the form:

```
ANOMSTACK__<METRIC_BATCH>__<PARAM>
```

- `<METRIC_BATCH>` is the `metric_batch` name from your YAML config, uppercased (replace dashes with underscores if present).
- `<PARAM>` is the config parameter name, uppercased (use underscores, e.g. `ALERT_METHODS`).

**Example:**

Suppose your metric batch config contains:

```yaml
metric_batch: "python_ingest_simple"
db: "duckdb"
alert_methods: "email,slack"
ingest_cron_schedule: "*/2 * * * *"
```

To override these via environment variables, add to your `.env` file:

```
ANOMSTACK__PYTHON_INGEST_SIMPLE__DB=bigquery
ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_METHODS=email
ANOMSTACK__PYTHON_INGEST_SIMPLE__INGEST_CRON_SCHEDULE=*/1 * * * *
```

This will override the `db`, `alert_methods`, and `ingest_cron_schedule` parameters for the `python_ingest_simple` metric batch at runtime, without changing the YAML file.

This makes it easy to manage config via environment variables for different deployments or local development.

## Properties

Key configuration properties:
- `name`: Metric identifier
- `description`: Metric description
- `source`: Data source configuration
- `schedule`: Execution schedule
- `alerts`: Alert settings

## Examples

Coming soon...

## Best Practices

Coming soon...
