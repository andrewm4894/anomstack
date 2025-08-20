# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Anomstack is an open-source anomaly detection system built on Dagster and FastHTML. It provides ML-powered anomaly detection for metrics from various data sources (BigQuery, Snowflake, ClickHouse, DuckDB, SQLite, etc.) with built-in alerting via email/Slack.

## Development Commands

### Local Development
- `make local` - Start Dagster locally with dev setup
- `make dashboard` - Start FastHTML dashboard locally (port 5003)
- `make dashboard-uvicorn` - Start dashboard with uvicorn (hot reload)
- `make dashboard-local-dev` - Start dashboard with seeded test data
- `make dev` - Setup local development environment and install dependencies

### Docker Operations
- `make docker` - Start all services with Docker Compose
- `make docker-dev` - Start with local development images  
- `make docker-smart` - Build fresh images and start containers
- `make docker-build` - Build all images locally
- `make docker-logs` - View logs for all containers
- `make docker-logs-<service>` - View logs for specific service (code, dagit, dashboard, daemon)
- `make docker-shell-<service>` - Get shell access to running containers
- `make docker-restart` - Restart all containers (useful for .env changes)
- `make docker-stop` - Stop all containers

### Testing & Quality
- `pytest` or `make tests` - Run test suite
- `make pre-commit` - Run pre-commit hooks (ruff linting)
- `make coverage` - Run tests with coverage report

### Database Seeding
- `make seed-local-db` - Seed local DB with python_ingest_simple data
- `make seed-local-db-all` - Seed with all example metric batches
- `make seed-local-db-custom BATCHES='batch1,batch2' DB_PATH='path/to/db'`

### Configuration & Hot Reload
- `make reload-config` - Reload configuration without restarting containers
- `make enable-auto-reload` - Enable automatic config reloading
- `make enable-config-watcher` - Enable smart config file watcher

### Reset & Cleanup Operations
- `make reset-interactive` - Interactive reset with guided options
- `make reset-gentle` - Rebuild containers (safest reset)
- `make reset-nuclear` - Remove everything including data
- `make dagster-cleanup-standard` - Clean up old Dagster runs

## Architecture

### Core Components
- **anomstack/**: Main application code
  - `main.py`: Dagster definitions and job orchestration
  - `config.py`: Configuration management
  - `jobs/`: Dagster jobs (ingest, train, score, alert, plot)
  - `ml/`: Machine learning components (PyOD models)
  - `external/`: Database connectors (BigQuery, Snowflake, etc.)
  - `alerts/`: Email/Slack alerting system
- **dashboard/**: FastHTML web dashboard with MonsterUI
- **metrics/**: Metric batch configurations (.yaml) and SQL queries (.sql)
  - `defaults/`: Default configuration parameters
  - `examples/`: Example metric batches for various data sources

### Metric Batch System
Metrics are organized into "batches" - collections of related metrics with shared configuration. Each batch requires:
- `.yaml` config file defining parameters (database, schedule, alert methods)
- `.sql` file with query OR custom Python ingest function
- Optional custom preprocessing functions

### Jobs Workflow
1. **Ingest**: Run SQL/Python to collect metrics
2. **Train**: Train PyOD anomaly detection models
3. **Score**: Score new data points for anomalies  
4. **Alert**: Send email/Slack alerts for detected anomalies
5. **Plot**: Generate visualizations in Dagster UI

### Database Storage
All data stored in long-format "metrics" table with columns:
- `metric_timestamp`, `metric_batch`, `metric_name`, `metric_type`, `metric_value`
- `metric_type` can be: 'metric' (raw data), 'score' (anomaly score), 'alert' (alert flag)

## Configuration

### Environment Files
- `.env`: Main environment configuration
- `profiles/`: Environment profiles for different deployments
  - `local-dev.env`: Local development with simple examples
  - `demo.env`: Demo configuration for Fly.io deployment
  - `production.env`: Production settings

### Override Pattern
Environment variables can override metric batch config using pattern:
`ANOMSTACK__<METRIC_BATCH>__<PARAM>` (uppercase, underscores for dashes)

Example:
```bash
ANOMSTACK__PYTHON_INGEST_SIMPLE__DB=bigquery
ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_METHODS=email
```

## Key Files to Know

### Configuration
- `dagster.yaml`: Dagster configuration
- `metrics/defaults/defaults.yaml`: Default parameters for all metric batches
- `pyproject.toml`: Ruff linting configuration

### Entry Points  
- `anomstack/main.py`: Main Dagster definitions
- `dashboard/app.py`: FastHTML dashboard application

### Database Connectors
- `anomstack/external/`: Connectors for BigQuery, Snowflake, ClickHouse, DuckDB, SQLite

## Development Notes

### Important Development Rule
**ALWAYS check the Makefile first** when working on Anomstack! The project includes comprehensive Make commands for all common development tasks. Before running manual commands, review the available Makefile commands.

### Code Style
- Uses ruff for linting (line length: 100)
- Star imports allowed in dashboard modules (F403/F405 rules ignored)
- Pre-commit hooks enforce code quality
- Per-file lint ignores configured for dashboard routes and maintenance scripts

### Testing
- Tests in `tests/` directory
- Use `pytest` or `make tests` for running tests
- `make test-examples` - Run only example ingest function tests
- Test coverage tracking with badges in README

### Deployment Options
- Local Python environment
- Docker Compose (recommended for development)
- Fly.io (production deployment)
- Dagster Cloud (serverless)
- GitHub Codespaces

### Metric Examples
The `metrics/examples/` directory contains ready-to-use examples:
- HackerNews story metrics via API
- Weather data from Open Meteo
- Stock prices from Yahoo Finance
- System metrics from Netdata
- Simple Python-generated test metrics

When adding new metrics, follow existing patterns in examples and ensure proper `.yaml` configuration with required fields like `metric_batch`, `db`, and cron schedules.