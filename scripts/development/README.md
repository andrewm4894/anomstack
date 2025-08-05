# Local Development Scripts

This directory contains scripts to help with local development of Anomstack.

## Database Seeding for Dashboard Development

### `seed_local_db.py`

Seeds a local DuckDB database with dummy metric data for dashboard development. This allows you to quickly iterate on the dashboard UI without needing to set up a full Dagster pipeline or wait for real data ingestion.

**Features:**
- Generates historical data using the `python_ingest_simple` ingest function
- Creates realistic metric data with occasional anomalies (spikes, drops, plateaus)
- Configurable time range and data interval
- Proper database schema matching production expectations
- Performance indexes for fast dashboard queries

**Usage:**
```bash
# Using make command (recommended)
make seed-local-db

# Or directly with custom options
python scripts/development/seed_local_db.py --hours 48 --interval 15 --force

# Help
python scripts/development/seed_local_db.py --help
```

**Options:**
- `--db-path`: Database file path (default: `tmpdata/anomstack-local-dev.db`)
- `--hours`: Hours of historical data (default: 72)
- `--interval`: Minutes between data points (default: 10)
- `--force`: Overwrite existing database

### `test_local_dev_db.py`

Validates that the seeded database works correctly with the dashboard.

**Tests performed:**
- Database connectivity
- Table existence and data availability
- Dashboard-compatible queries
- Data variety and anomaly detection

**Usage:**
```bash
python scripts/development/test_local_dev_db.py
```

## Local Dashboard Development Workflow

### Quick Start
```bash
# 1. Seed the database (creates ~72 hours of dummy data)
make seed-local-db

# 2. Start dashboard in local dev mode
make dashboard-local-dev
```

### Manual Workflow
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Create database with custom settings
python scripts/development/seed_local_db.py --hours 24 --interval 5 --force

# 3. Test the database
python scripts/development/test_local_dev_db.py

# 4. Start dashboard with custom database
ANOMSTACK_DUCKDB_PATH=tmpdata/anomstack-local-dev.db uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload
```

### Generated Data Structure

The seeded database contains:
- **Table**: `metrics_python_ingest_simple`
- **Metrics**: `metric1`, `metric2`, `metric3`, `metric4`, `metric5`
- **Data Types**: Normal values (0-10), spikes (15-30), drops (-10 to -1), plateaus (5-6)
- **Anomaly Rate**: ~1% chance per data point
- **Schema**: Compatible with Anomstack production database schema

### Dashboard Access

Once running, access the dashboard at:
- **URL**: http://localhost:5003
- **Metric Batch**: `python_ingest_simple`
- **Data Range**: Last 72 hours (configurable)

### Tips for Dashboard Development

1. **Fast Iteration**: Use `--reload` flag for automatic dashboard restarts
2. **Data Variety**: The seeded data includes anomalies for testing alert visualizations
3. **Performance**: Database includes indexes for fast query performance
4. **Isolation**: Local dev database is separate from any production data
5. **Reset**: Use `make seed-local-db` to regenerate fresh data anytime

### Troubleshooting

**Database not found:**
```bash
make seed-local-db
```

**Dashboard connection issues:**
```bash
python scripts/development/test_local_dev_db.py
```

**Port conflicts:**
Change the port in the make command or set `ANOMSTACK_DASHBOARD_PORT` environment variable.

**Virtual environment issues:**
```bash
source venv/bin/activate
pip install -r requirements.txt
``` 