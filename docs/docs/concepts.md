---
sidebar_position: 3
---

# Core Concepts

This page explains the key concepts and terminology used in Anomstack.

## Metric Batch

A metric batch is the fundamental unit of configuration in Anomstack. It consists of:

- A configuration file (`config.yaml`)
- A SQL query file (`query.sql`) or Python ingest function
- Optional preprocessing function
- Optional custom configuration

Example structure:
```
metrics/
  my_metric_batch/
    config.yaml
    query.sql
    preprocess.py (optional)
```

## Jobs

Anomstack runs several types of jobs for each metric batch:

### Ingest Job
- Pulls data from your data source
- Executes your SQL query or Python function
- Stores raw data for processing

### Train Job
- Processes historical data
- Trains anomaly detection models
- Saves trained models to storage

### Score Job
- Applies trained models to new data
- Calculates anomaly scores
- Identifies potential anomalies

### Alert Job
- Evaluates anomaly scores
- Sends notifications via configured channels
- Handles alert throttling and snoozing

### Change Detection Job
- Monitors for significant changes in metrics
- Detects level shifts and trends
- Triggers alerts for important changes

### Plot Job
- Generates visualizations of metrics
- Creates anomaly score plots
- Produces plots for alerts and dashboard

## Alerts

Alerts are notifications sent when anomalies are detected. They can be configured to:

- Send via email or Slack
- Include visualizations
- Use custom templates
- Support different severity levels
- Include LLM-powered analysis

## Dashboard

The dashboard provides:

- Real-time metric visualization
- Anomaly score monitoring
- Alert history and management
- Metric configuration interface
- Performance analytics

## Storage

Anomstack uses storage for:

- Trained models
- Configuration files
- Alert history
- Performance metrics
- Dashboard data

Supported storage backends:
- Local filesystem
- Google Cloud Storage (GCS)
- Amazon S3
- Azure Blob Storage (coming soon)

## Data Sources

Anomstack supports various data sources:

- Python (direct integration)
- BigQuery
- Snowflake
- ClickHouse
- DuckDB
- SQLite
- MotherDuck
- Turso
- Redshift (coming soon)

## Configuration

Configuration is handled through:

- YAML files for metric batches
- Environment variables
- Command-line arguments
- Dashboard settings

## Scheduling

Jobs can be scheduled using:

- Cron expressions
- Dagster schedules
- Manual triggers
- Event-based triggers

## LLM Agent

The LLM agent provides:

- AI-powered anomaly analysis
- Natural language explanations
- Automated reporting
- Intelligent alert prioritization
- Historical context analysis
