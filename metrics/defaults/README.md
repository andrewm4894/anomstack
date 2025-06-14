# Anomstack Defaults Configuration

This directory contains the default configuration files and templates that serve as the foundation for the **Anomstack** anomaly detection system. Anomstack is a lightweight data app built on [Dagster](https://dagster.io/) and [FastHTML](https://fastht.ml/) that provides painless open source anomaly detection for your metrics using machine learning models from [PyOD](https://pyod.readthedocs.io/en/latest/).

These defaults are applied to all **metric batches** unless specifically overridden in individual metric batch configuration files, allowing you to easily customize behavior without modifying core code.

## Files Overview

### `defaults.yaml`
The comprehensive configuration file containing default settings for all Anomstack system components:

- **Database Configuration**: Multi-platform support (DuckDB, BigQuery, Snowflake, ClickHouse, SQLite, etc.)
- **Model Parameters**: PyOD model configurations (PCA, KNN), training parameters, and preprocessing settings
- **Alert System**: Email/Slack alert configurations, thresholds, snooze settings, and feedback systems  
- **Change Detection**: Parameters for detecting significant changes in time series data
- **LLM Alerts**: Configuration for AI-powered anomaly analysis using language models
- **Job Scheduling**: Cron schedules for all automated Dagster jobs (ingest, train, score, alert, etc.)
- **SQL Templates**: Jinja2 template references for dynamic SQL generation

### `python/` Directory

Contains Python modules and functions used throughout the Anomstack pipeline:

- **`preprocess.py`**: Time series preprocessing functions for ML model preparation:
  - Differencing and smoothing operations for noise reduction
  - Lag feature creation for temporal pattern detection
  - Data resampling and aggregation for different frequencies
  - Missing value handling and data validation

### `sql/` Directory

Contains Jinja2-templated SQL files for the core Anomstack jobs. These templates dynamically generate SQL based on configuration parameters and support multiple database dialects via SQLGlot:

- **`alerts.sql`**: Combines metric values, anomaly scores, and historical alerts to determine when to trigger notifications
- **`change.sql`**: Implements statistical change detection using PyOD's MAD (Median Absolute Deviation) method
- **`dashboard.sql`**: Provides data for the FastHTML/MonsterUI dashboard visualization
- **`delete.sql`**: Handles cleanup of old metric data based on configurable retention policies
- **`llmalert.sql`**: Prepares time series context for LLM-based anomaly analysis and alerting
- **`plot.sql`**: Generates data for time series visualizations in Dagster UI and dashboard
- **`score.sql`**: Retrieves recent metric data for anomaly scoring using trained models
- **`summary.sql`**: Creates daily summary reports of system activity and anomaly detection
- **`train.sql`**: Prepares training datasets for PyOD anomaly detection models

## Anomstack Architecture Integration

These defaults support Anomstack's core architecture where each **metric batch** goes through a pipeline of **Dagster jobs**:

1. **Ingest**: Pull metrics using SQL queries or custom Python functions
2. **Train**: Train PyOD models on historical data using these preprocessing defaults
3. **Score**: Generate anomaly scores using trained models
4. **Alert**: Send notifications when anomalies are detected
5. **Change**: Detect significant changes in metric patterns
6. **LLM Alert**: Use AI agents for intelligent anomaly analysis
7. **Plot**: Generate visualizations for monitoring

## Usage in Metric Batches

These defaults are automatically applied to all metric batches. To customize settings for a specific batch:

1. Create a YAML configuration file in the parent `metrics/` directory
2. Override only the parameters you want to change - all others inherit from these defaults
3. The system merges your custom settings with these defaults at runtime

Example metric batch structure:
```
metrics/
├── defaults/           # This directory
├── examples/          # Example metric batches
└── my_batch/
    ├── my_batch.yaml  # Custom config (overrides defaults)
    └── my_batch.sql   # Metric query
```

## Template System & Multi-Platform Support

The SQL templates use Jinja2 syntax and support Anomstack's multi-platform architecture:

- **Configuration Parameters**: Reference any setting from `defaults.yaml` (e.g., `{{ alert_threshold }}`)
- **Runtime Variables**: Use metric batch-specific variables (e.g., `{{ metric_batch }}`)
- **Conditional Logic**: Handle optional parameters (e.g., `{% if alert_exclude_metrics is defined %}`)
- **Database Translation**: Written for DuckDB but automatically translated to target dialects via SQLGlot

## Key Features

- **Zero-Config Start**: Sensible defaults for immediate productivity
- **Multi-Platform**: Support for major cloud databases and local storage
- **ML-Powered**: Integration with PyOD's extensive anomaly detection algorithms
- **Flexible Alerting**: Email, Slack, and LLM-based notification systems
- **Modern UI**: FastHTML dashboard with MonsterUI components
- **Production Ready**: Configurable retention, snoozing, and feedback systems

For more details on setting up metric batches and customizing Anomstack, see the main project documentation and examples in the [`metrics/examples/`](../examples/) directory. 