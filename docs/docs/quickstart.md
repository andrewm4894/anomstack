---
sidebar_position: 2
---

# Quickstart Guide

Get Anomstack up and running in minutes! This guide shows you the fastest way to start detecting anomalies in your metrics.

## 🐳 Recommended: Docker Setup (Easiest!)

**Why Docker?** Zero dependency conflicts, isolated environment, and works consistently everywhere. This is by far the easiest way to get started!

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/andrewm4894/anomstack.git
cd anomstack

# Copy the example environment file
cp .example.env .env

# Start Anomstack with Docker (uses pre-built images from Docker Hub)
make docker
```

That's it! 🎉 Anomstack is now running:
- **Dagster UI**: http://localhost:3000 (orchestration & job management)
- **Dashboard**: http://localhost:5001 (metrics visualization & anomalies)

### What just happened?
- Docker automatically downloaded pre-built images from Docker Hub
- PostgreSQL database started for Dagster metadata
- DuckDB volume created for persistent metrics storage
- Example metrics are already configured and ready to run
- Both the Dagster backend and FastHTML dashboard are running

### Next Steps with Docker
1. **Enable example jobs** in the Dagster UI at http://localhost:3000
   - Navigate to "Deployment" → Find metric batches like `currency`, `weather`, etc.
   - Turn on schedules or click "Materialize" to run jobs manually
2. **Wait for data** - Let it run for 10-15 minutes to collect example metrics
3. **View your dashboard** at http://localhost:5001 to see metrics and detected anomalies
4. **Check logs** if needed: `make docker-logs`

### Useful Docker Commands
```bash
make docker               # Start with pre-built images (recommended)
make docker-dev          # Start with locally built images (for development)
make docker-smart        # Smart start (tries pull, falls back to build)
make docker-logs         # View all container logs
make docker-stop         # Stop all services
make reset-interactive   # Interactive cleanup with guided options
```

> 💡 **For comprehensive Docker documentation**, see [DOCKER.md](https://github.com/andrewm4894/anomstack/blob/main/DOCKER.md) which covers volumes, networking, troubleshooting, production considerations, and more.

---

## 🐍 Alternative: Local Python Setup

If you prefer to run Anomstack directly with Python (useful for development or when Docker isn't available):

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Steps
```bash
# Clone the repository
git clone https://github.com/andrewm4894/anomstack.git
cd anomstack

# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .example.env .env
# Edit .env to set ANOMSTACK_DUCKDB_PATH=tmpdata/anomstack-duckdb.db for local dev

# Start Dagster
dagster dev -f anomstack/main.py
```

**Dagster UI** will be available at http://localhost:3000.

**Dashboard** (in a separate terminal):
```bash
# Activate your virtual environment first
source .venv/bin/activate

# Start dashboard
python dashboard/app.py
```

The dashboard will be available at http://localhost:5001.

---

## 🚀 Try Some Example Metrics

Anomstack comes with ready-to-use example metrics so you can see it in action immediately:

### Popular Examples
- **[Currency Rates](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/currency)** - Track exchange rates from public APIs
- **[Yahoo Finance](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/yfinance)** - Monitor stock prices and financial data
- **[Weather Data](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/weather)** - Analyze weather patterns from Open Meteo
- **[Hacker News](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples/hackernews)** - Track story scores and trends

### How to Enable Examples

1. **In Dagster UI** (http://localhost:3000):
   - Go to **"Deployment"** in the left sidebar
   - Find schedules like `currency_ingest_schedule`, `weather_ingest_schedule`, etc.
   - **Turn on schedules** by clicking the toggle, or
   - Go to **"Jobs"** and click **"Materialize"** to run them manually

2. **Wait for data to collect** (10-15 minutes for meaningful results)

3. **Check the dashboard** (http://localhost:5001) to see your metrics and any detected anomalies

See the [full list of examples](https://github.com/andrewm4894/anomstack/tree/main/metrics/examples) for BigQuery, Snowflake, Prometheus, and more!

---

## 🔧 Adding Your Own Metrics

Once you're comfortable with the examples, add your own metrics:

### 1. Create a Metric Batch Directory
```bash
mkdir -p metrics/my_custom_metric
```

### 2. Define Your Metric
Create either a **SQL file** or **Python function**:

**Option A: SQL** (`metrics/my_custom_metric/query.sql`):
```sql
SELECT
    CURRENT_TIMESTAMP as metric_timestamp,
    'my_metric' as metric_name,
    COUNT(*) as metric_value
FROM your_table
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
```

**Option B: Python** (`metrics/my_custom_metric/ingest.py`):
```python
import pandas as pd
from datetime import datetime

def ingest():
    # Your custom logic here
    data = {
        'metric_timestamp': [datetime.now()],
        'metric_name': ['my_metric'],
        'metric_value': [42]
    }
    return pd.DataFrame(data)
```

### 3. Create Configuration
Create `metrics/my_custom_metric/my_custom_metric.yaml`:
```yaml
metric_batch: my_custom_metric
db: duckdb  # or bigquery, snowflake, clickhouse, sqlite, etc.

# For SQL approach:
ingest_sql: query.sql

# For Python approach:
# ingest_fn: ingest.py

ingest_cron_schedule: "*/10 * * * *"  # Every 10 minutes
alert_methods: email  # Configure in .env file
```

### 4. Restart and Enable
- **Docker**: `make docker-stop && make docker`
- **Python**: Restart your `dagster dev` process

Then enable your new metric batch schedules in the Dagster UI!

---

## 📊 Understanding the Workflow

Anomstack follows a simple 5-step process for each metric batch:

1. **Ingest** - Collect your metrics from various data sources
2. **Train** - Build ML models on historical data (needs ~20+ data points)
3. **Score** - Detect anomalies in new data using trained models  
4. **Alert** - Notify you when anomalies are found (email/Slack)
5. **Dashboard** - Visualize everything in one place

Each step runs as a separate Dagster job that you can monitor and control independently.

---

## 🆘 Troubleshooting

### Docker Issues
```bash
# Check if containers are running
docker compose ps

# View logs for all services
make docker-logs

# View logs for specific service
make docker-logs-code      # Code server logs
make docker-logs-dashboard # Dashboard logs

# Restart everything
make docker-stop && make docker

# Interactive reset with options
make reset-interactive
```

### Common Questions

**Q: No data showing in dashboard?**  
A: Wait 10-15 minutes for ingest jobs to run and collect data. Check job status in Dagster UI.

**Q: Jobs failing in Dagster?**  
A: Check the job logs in Dagster UI for specific error messages. Most failures are due to missing environment variables or network connectivity. Use `python scripts/kill_long_running_tasks.py` to clean up stuck jobs.

**Q: Port already in use?**  
A: Stop other services on ports 3000 or 5001, or change ports in `docker-compose.yaml`.

**Q: Want to add email/Slack alerts?**  
A: Configure your `.env` file with email/Slack credentials. See [alerts documentation](features/alerts) and [environment variables](configuration/environment-variables).

**Q: How do I connect to my own database?**  
A: Set up the appropriate connection in your `.env` file (BigQuery, Snowflake, etc.) and reference it in your metric batch YAML files. See the full [environment variables guide](configuration/environment-variables) for all database options.

---

## 🎯 Next Steps

Now that you're up and running:

1. **[Learn the core concepts](concepts)** - Understand metric batches, jobs, and the ML workflow
2. **[Configure environment variables](configuration/environment-variables)** - Set up database connections, alerts, and advanced options
3. **[Configure alerts](features/alerts)** - Get notified of anomalies via email/Slack  
4. **[Explore data sources](data-sources)** - Connect to BigQuery, Snowflake, ClickHouse, and more
5. **[Deploy to production](deployment/)** - Use Dagster Cloud, scale with Docker, or deploy on your infrastructure

---

## 💬 Need Help?

- **[GitHub Issues](https://github.com/andrewm4894/anomstack/issues)** - Report bugs or request features
- **[GitHub Discussions](https://github.com/andrewm4894/anomstack/discussions)** - Ask questions and share ideas  
- **[Scripts & Utilities](miscellaneous/scripts-utilities)** - Handy tools for maintenance and troubleshooting
- **[DOCKER.md](https://github.com/andrewm4894/anomstack/blob/main/DOCKER.md)** - Comprehensive Docker documentation
- **[Full Documentation](intro)** - Complete guide to all features
