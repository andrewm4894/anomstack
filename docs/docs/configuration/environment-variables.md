---
sidebar_position: 1
---

# Environment Variables

This page documents all environment variables available in Anomstack. Copy the [`.example.env`](https://github.com/andrewm4894/anomstack/blob/main/.example.env) file to `.env` and configure the variables you need.

```bash
cp .example.env .env
```

## 🗄️ Database & Data Sources

### Google Cloud Platform
Configure access to BigQuery and Google Cloud Storage.

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS` | No | Path to GCP service account JSON file | `/path/to/credentials.json` |
| `ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS_JSON` | No | GCP credentials as JSON string (alternative to file path) | `{"type": "service_account", ...}` |
| `ANOMSTACK_GCP_PROJECT_ID` | No | Google Cloud Project ID for BigQuery | `my-project-123` |

### Snowflake
Connect to Snowflake data warehouse.

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ANOMSTACK_SNOWFLAKE_ACCOUNT` | No | Snowflake account identifier | `xy12345.us-east-1` |
| `ANOMSTACK_SNOWFLAKE_USER` | No | Snowflake username | `anomstack_user` |
| `ANOMSTACK_SNOWFLAKE_PASSWORD` | No | Snowflake password | `your-password` |
| `ANOMSTACK_SNOWFLAKE_WAREHOUSE` | No | Snowflake warehouse name | `ANOMSTACK_WH` |

### AWS
Connect to S3 and other AWS services.

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ANOMSTACK_AWS_ACCESS_KEY_ID` | No | AWS access key ID | `AKIAIOSFODNN7EXAMPLE` |
| `ANOMSTACK_AWS_SECRET_ACCESS_KEY` | No | AWS secret access key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |

### ClickHouse
Connect to ClickHouse database.

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_CLICKHOUSE_HOST` | No | ClickHouse host | `localhost` | `clickhouse.example.com` |
| `ANOMSTACK_CLICKHOUSE_PORT` | No | ClickHouse port | `8123` | `8123` |
| `ANOMSTACK_CLICKHOUSE_USER` | No | ClickHouse username | `anomstack` | `admin` |
| `ANOMSTACK_CLICKHOUSE_PASSWORD` | No | ClickHouse password | `anomstack` | `your-password` |
| `ANOMSTACK_CLICKHOUSE_DATABASE` | No | ClickHouse database | `default` | `metrics` |

### MotherDuck & Turso
Enhanced DuckDB and SQLite services.

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ANOMSTACK_MOTHERDUCK_TOKEN` | No | MotherDuck authentication token | `your-motherduck-token` |
| `ANOMSTACK_TURSO_DATABASE_URL` | No | Turso database URL | `libsql://your-db.turso.io` |
| `ANOMSTACK_TURSO_AUTH_TOKEN` | No | Turso authentication token | `your-turso-token` |

## 💾 Storage Configuration

### Database Paths
Configure where metrics and metadata are stored.

| Variable | Required | Description | Docker Default | Local Default |
|----------|----------|-------------|---------------|---------------|
| `ANOMSTACK_DUCKDB_PATH` | No | DuckDB database path | `/data/anomstack.db` | `tmpdata/anomstack-duckdb.db` |
| `ANOMSTACK_SQLITE_PATH` | No | SQLite database path | `tmpdata/anomstack-sqlite.db` | `tmpdata/anomstack-sqlite.db` |
| `ANOMSTACK_TABLE_KEY` | No | Table identifier for metrics | `tmp.metrics` | `production.metrics` |

### Model Storage
Configure where trained ML models are stored.

| Variable | Required | Description | Examples |
|----------|----------|-------------|----------|
| `ANOMSTACK_MODEL_PATH` | No | Model storage location | `local://./tmp/models`<br/>`gs://your-bucket/models`<br/>`s3://your-bucket/models` |

**Storage Options:**
- **Local**: `local://./tmp/models` (default)
- **Google Cloud Storage**: `gs://your-bucket/models`
- **AWS S3**: `s3://your-bucket/models`

### Application Paths
Internal directory configuration.

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ANOMSTACK_HOME` | No | Home directory for Anomstack | `.` (current directory) |

## 📧 Alert Configuration

### Email Alerts
Configure email notifications for anomalies.

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_ALERT_EMAIL_FROM` | No | Sender email address | | `alerts@yourcompany.com` |
| `ANOMSTACK_ALERT_EMAIL_TO` | No | Recipient email address | | `team@yourcompany.com` |
| `ANOMSTACK_ALERT_EMAIL_SMTP_HOST` | No | SMTP server host | `smtp.gmail.com` | `smtp.office365.com` |
| `ANOMSTACK_ALERT_EMAIL_SMTP_PORT` | No | SMTP server port | `587` | `25` |
| `ANOMSTACK_ALERT_EMAIL_PASSWORD` | No | Email password/app token | | `your-app-password` |

### Failure Email Alerts
Separate email configuration for job failures.

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ANOMSTACK_FAILURE_EMAIL_FROM` | No | Sender for failure alerts | `failures@yourcompany.com` |
| `ANOMSTACK_FAILURE_EMAIL_TO` | No | Recipient for failure alerts | `ops@yourcompany.com` |
| `ANOMSTACK_FAILURE_EMAIL_SMTP_HOST` | No | SMTP host for failures | `smtp.gmail.com` |
| `ANOMSTACK_FAILURE_EMAIL_SMTP_PORT` | No | SMTP port for failures | `587` |
| `ANOMSTACK_FAILURE_EMAIL_PASSWORD` | No | Email password for failures | `your-app-password` |

### Slack Alerts
Configure Slack notifications.

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ANOMSTACK_SLACK_BOT_TOKEN` | No | Slack bot token | `xoxb-your-bot-token` |
| `ANOMSTACK_SLACK_CHANNEL` | No | Slack channel for alerts | `#anomaly-alerts` |

## 🤖 LLM Integration

### OpenAI
Configure AI-powered anomaly detection and alerts.

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_OPENAI_KEY` | No | OpenAI API key | | `sk-...` |
| `OPENAI_API_KEY` | No | Alternative OpenAI API key | | `sk-...` |
| `ANOMSTACK_OPENAI_MODEL` | No | OpenAI model to use | `gpt-4o-mini` | `gpt-4o` |

### Anthropic
Alternative LLM provider.

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_ANTHROPIC_KEY` | No | Anthropic API key | | `sk-ant-...` |
| `ANOMSTACK_ANTHROPIC_MODEL` | No | Anthropic model | `claude-3-haiku-20240307` | `claude-3-sonnet-20240229` |

### LLM Platform Selection

| Variable | Required | Description | Default | Options |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_LLM_PLATFORM` | No | Which LLM provider to use | `openai` | `openai`, `anthropic` |

### LangSmith Tracing
Optional LLM call tracing and monitoring.

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `LANGSMITH_TRACING` | No | Enable LangSmith tracing | `true` | `false` |
| `LANGSMITH_ENDPOINT` | No | LangSmith API endpoint | `https://api.smith.langchain.com` | |
| `LANGSMITH_API_KEY` | No | LangSmith API key | | `your-api-key` |
| `LANGSMITH_PROJECT` | No | LangSmith project name | `anomaly-agent` | `your-project` |

## ⚙️ Dagster Configuration

### Core Dagster Settings

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `DAGSTER_LOG_LEVEL` | No | Dagster logging level | `DEBUG` | `INFO`, `WARNING`, `ERROR` |
| `DAGSTER_CONCURRENCY` | No | Number of concurrent jobs | `4` | `8` |

### Dagster Directories
Lightweight defaults to prevent disk space issues.

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ANOMSTACK_DAGSTER_LOCAL_ARTIFACT_STORAGE_DIR` | No | Artifacts storage directory | `tmp_light/artifacts` |
| `ANOMSTACK_DAGSTER_OVERALL_CONCURRENCY_LIMIT` | No | Overall concurrency limit | `5` |
| `ANOMSTACK_DAGSTER_DEQUEUE_USE_THREADS` | No | Use threads for dequeuing | `false` |
| `ANOMSTACK_DAGSTER_DEQUEUE_NUM_WORKERS` | No | Number of dequeue workers | `2` |
| `ANOMSTACK_DAGSTER_LOCAL_COMPUTE_LOG_MANAGER_DIRECTORY` | No | Compute logs directory | `tmp_light/compute_logs` |
| `ANOMSTACK_DAGSTER_SQLITE_STORAGE_BASE_DIR` | No | SQLite storage base directory | `tmp_light/storage` |

### Job Timeout Configuration

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_MAX_RUNTIME_SECONDS_TAG` | No | Max job runtime in seconds | `900` | `1800` |
| `ANOMSTACK_KILL_RUN_AFTER_MINUTES` | No | Kill long-running jobs after N minutes | `15` | `30` |

## 🐳 Docker & Deployment

### PostgreSQL (Docker)
Database for Dagster metadata when using Docker.

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ANOMSTACK_POSTGRES_USER` | No | PostgreSQL username | `postgres_user` |
| `ANOMSTACK_POSTGRES_PASSWORD` | No | PostgreSQL password | `postgres_password` |
| `ANOMSTACK_POSTGRES_DB` | No | PostgreSQL database name | `postgres_db` |
| `ANOMSTACK_POSTGRES_FORWARD_PORT` | No | Local port forwarding | `5432` (leave blank to disable) |

### Dashboard Configuration

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ANOMSTACK_DASHBOARD_PORT` | No | Dashboard port | `5001` |

## 🔧 Advanced Configuration

### Example Metrics

| Variable | Required | Description | Default | Options |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_IGNORE_EXAMPLES` | No | Ignore example metrics | `no` | `yes`, `no` |

### Auto-Reload Configuration
Automatically reload configuration when files change.

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `ANOMSTACK_AUTO_CONFIG_RELOAD` | No | Enable scheduled config reload | `false` | `true` |
| `ANOMSTACK_CONFIG_RELOAD_CRON` | No | Config reload schedule | `*/5 * * * *` | `*/10 * * * *` |
| `ANOMSTACK_CONFIG_RELOAD_STATUS` | No | Config reload job status | `STOPPED` | `RUNNING` |
| `ANOMSTACK_CONFIG_WATCHER` | No | Enable smart file watcher | `true` | `false` |
| `ANOMSTACK_CONFIG_WATCHER_INTERVAL` | No | File watcher check interval (seconds) | `30` | `60` |

### Analytics

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `POSTHOG_API_KEY` | No | PostHog analytics API key | `phc_...` |

## 🎛️ Per-Metric Batch Overrides

You can override any configuration parameter for specific metric batches using environment variables:

```bash
ANOMSTACK__<METRIC_BATCH>__<PARAMETER>=<VALUE>
```

**Format Rules:**
- `<METRIC_BATCH>`: Uppercase metric batch name with dashes replaced by underscores
- `<PARAMETER>`: Uppercase parameter name with underscores

**Examples:**
```bash
# Override database for python_ingest_simple metric batch
ANOMSTACK__PYTHON_INGEST_SIMPLE__DB=bigquery

# Override alert methods
ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_METHODS=email

# Override schedule
ANOMSTACK__PYTHON_INGEST_SIMPLE__INGEST_CRON_SCHEDULE="*/1 * * * *"

# Enable specific job schedules
ANOMSTACK__PYTHON_INGEST_SIMPLE__INGEST_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__PYTHON_INGEST_SIMPLE__TRAIN_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__PYTHON_INGEST_SIMPLE__SCORE_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_DEFAULT_SCHEDULE_STATUS=RUNNING
```

This allows you to configure different metric batches differently without modifying YAML files.

## 📝 Common Configuration Patterns

### Development Setup
```bash
# Use local storage
ANOMSTACK_DUCKDB_PATH=tmpdata/anomstack-duckdb.db
ANOMSTACK_MODEL_PATH=local://./tmp/models
ANOMSTACK_IGNORE_EXAMPLES=no

# Basic email alerts
ANOMSTACK_ALERT_EMAIL_FROM=dev@company.com
ANOMSTACK_ALERT_EMAIL_TO=developer@company.com
```

### Production Setup
```bash
# Use cloud storage
ANOMSTACK_MODEL_PATH=gs://company-anomstack/models
ANOMSTACK_DUCKDB_PATH=/data/anomstack.db

# Production alerts
ANOMSTACK_ALERT_EMAIL_FROM=alerts@company.com
ANOMSTACK_ALERT_EMAIL_TO=ops-team@company.com
ANOMSTACK_SLACK_CHANNEL=#production-alerts

# Disable examples
ANOMSTACK_IGNORE_EXAMPLES=yes
```

### BigQuery + GCS Setup
```bash
# BigQuery connection
ANOMSTACK_GCP_PROJECT_ID=your-project-id
ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Use GCS for model storage
ANOMSTACK_MODEL_PATH=gs://your-bucket/models

# BigQuery table for metrics
ANOMSTACK_TABLE_KEY=your_dataset.metrics
```

## 🔐 Security Best Practices

1. **Use environment files**: Never commit `.env` files with secrets to version control
2. **Rotate credentials**: Regularly rotate API keys and passwords
3. **Least privilege**: Use service accounts with minimal required permissions
4. **Secrets management**: Consider using proper secrets management in production (AWS Secrets Manager, Google Secret Manager, etc.)
5. **File permissions**: Restrict access to your `.env` file (`chmod 600 .env`)

## 🆘 Troubleshooting

**Environment not loading?**
- Ensure `.env` file exists in the project root
- Check file permissions and syntax
- Verify no extra spaces around `=` signs

**Docker not picking up changes?**
- Restart containers: `make docker-stop && make docker`
- Check if environment is properly mounted

**Database connection issues?**
- Verify credentials and network access
- Test connections independently
- Check firewall and VPN settings
