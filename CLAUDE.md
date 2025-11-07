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
- `pytest` or `make tests` - Run test suite (includes documentation link checking)
- `make test-examples` - Run only example ingest function tests
- `make coverage` - Run tests with coverage report
- `make pre-commit` - Run pre-commit hooks (ruff linting)

### Documentation Commands
- `make docs` or `make docs-start` - Start Docusaurus dev server with live reload
- `make docs-build` - Build static documentation site (includes broken link checking)
- `make docs-test` - Test documentation for broken links
- `make docs-serve` - Serve built documentation locally
- `make docs-clear` - Clear documentation build cache
- `make docs-install` - Install documentation dependencies

### Database Seeding & Examples
- `make seed-local-db` - Seed local DB with python_ingest_simple data
- `make seed-local-db-all` - Seed with all example metric batches
- `make seed-local-db-custom BATCHES='batch1,batch2' DB_PATH='path/to/db'`
- `make run-example EXAMPLE=<name>` - Test individual example ingest functions
- `make list-examples` - List all 26+ available examples

### Configuration & Hot Reload
- `make reload-config` - Reload configuration without restarting containers
- `make enable-auto-reload` - Enable automatic config reloading
- `make enable-config-watcher` - Enable smart config file watcher

### Reset & Cleanup Operations
- `make reset-interactive` - Interactive reset with guided options
- `make reset-gentle` - Rebuild containers (safest reset)
- `make reset-medium` - Remove containers, keep data volumes
- `make reset-nuclear` - Remove everything including local data
- `make reset-full-nuclear` - Nuclear + full docker system cleanup (maximum cleanup)
- `make dagster-cleanup-status` - Show current Dagster storage usage
- `make dagster-cleanup-minimal` - Remove old logs only (safe)
- `make dagster-cleanup-standard` - Clean up old Dagster runs (older than 30 days)
- `make dagster-cleanup-aggressive` - Remove runs older than 7 days
- `make kill-long-runs` - Manually kill any Dagster runs exceeding configured timeout

### Fly.io Deployment Commands
- `make fly-preview` - Preview environment variables that will be set as Fly secrets
- `make fly-deploy` - Deploy to Fly.io (reads .env file automatically)
- `make fly-deploy-demo` - Deploy with demo profile (enables demo metric batches)
- `make fly-deploy-production` - Deploy with production profile
- `make fly-deploy-development` - Deploy with development profile (all examples enabled)
- `make fly-deploy-demo-fresh` - Deploy with fresh build (clears Docker cache first)
- `make fly-build-test` - Test Fly.io build locally before deploying
- `make fly-docker-clean` - Clean Docker cache for Fly builds
- `make fly-cleanup` - Run disk cleanup on Fly instance (requires SSH access)
- `make fly-cleanup-preview` - Preview cleanup on Fly instance (dry run)
- `make fly-status` - Check Fly.io app status (requires FLY_APP env var)
- `make fly-logs` - View Fly.io app logs (requires FLY_APP env var)
- `make fly-ssh` - SSH into Fly.io app (requires FLY_APP env var)

### Render.com Deployment Commands

**API Deployment** (no GitHub commit needed):
- `make render-demo-deploy` - Deploy demo instance via Render API
- `make render-production-deploy` - Deploy production instance via Render API
- `make render-development-deploy` - Deploy development instance via Render API

**Blueprint Deployment** (requires GitHub commit):
- `make render-validate` - Validate render.yaml configuration
- `make render-deploy` - Deploy using Blueprint (shows deployment instructions)

**Management**:
- `make render-services` - List all Render services
- `make render-logs` - View service logs (requires RENDER_SERVICE_ID env var)
- `make render-shell` - SSH into running service (requires RENDER_SERVICE_ID env var)

**Quick Start (API Deployment):**
1. Get API key: https://dashboard.render.com/u/settings#api-keys
2. Add to .env: `RENDER_API_KEY=rnd_xxx...`
3. Run: `make render-demo-deploy`
4. Set `ANOMSTACK_ADMIN_PASSWORD` secret in Render Dashboard
5. See `docs/render-deployment.md` for detailed instructions

## Architecture

### Container Architecture
Anomstack uses a simplified 3-container Docker architecture:
- **anomstack_webserver**: Consolidated Dagster webserver with embedded user code (no separate gRPC server)
- **anomstack_daemon**: Dagster daemon for job scheduling and execution
- **anomstack_dashboard**: FastHTML dashboard for metrics visualization

This consolidated approach eliminates the previous gRPC code server, reducing network overhead and improving reliability through direct Python module loading.

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
5. **LLM Alert**: LLM-based anomaly detection and alerting using anomaly-agent
6. **Plot**: Generate visualizations in Dagster UI
7. **Change**: Change detection for metrics
8. **Summary**: Daily summary emails
9. **Delete**: Delete old metrics
10. **Reload**: Configuration hot-reload job
11. **Cleanup**: Disk space management
12. **Retention**: Custom retention for SQLite

### Dagster Sensors
Three key sensors monitor the system:
1. **email_on_run_failure**: Sends email notifications when Dagster runs fail
2. **kill_long_running_runs**: Automatically terminates runs exceeding configured timeout (default 15 minutes, configurable via `ANOMSTACK_KILL_RUN_AFTER_MINUTES`)
3. **config_file_watcher**: Smart file watcher that detects configuration changes and triggers reloads (enabled via `ANOMSTACK_CONFIG_WATCHER=true`)

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
- `anomstack/main.py`: Main Dagster definitions (defines all jobs, schedules, and sensors)
- `dashboard/app.py`: FastHTML dashboard application
- `anomstack/config.py`: Configuration loading and environment variable override logic

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
- Test coverage tracking with badges in README
- See "Testing & Quality" section for test commands

### Deployment Options
- Local Python environment
- Docker Compose (recommended for development)
- Fly.io (production deployment)
- Render.com (production deployment with Blueprint)
- Dagster Cloud (serverless)
- GitHub Codespaces

### Metric Examples
The `metrics/examples/` directory contains ready-to-use examples:
- HackerNews story metrics via API
- Weather data from Open Meteo
- Stock prices from Yahoo Finance (yfinance)
- System metrics from Netdata
- Simple Python-generated test metrics (python_ingest_simple)
- Earthquake data from USGS
- ISS location tracking
- PostHog analytics (requires credentials)
- Currency exchange rates
- And 26+ total examples

When adding new metrics, follow existing patterns in examples and ensure proper `.yaml` configuration with required fields like `metric_batch`, `db`, and cron schedules.

Use `make run-example EXAMPLE=<name>` to test individual examples or `make list-examples` to see all available examples.