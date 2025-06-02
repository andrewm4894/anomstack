---
sidebar_position: 1
---

# Introduction to Anomstack

Anomstack is an open-source anomaly detection platform that makes it easy to monitor and detect anomalies in your metrics data. Built on top of [Dagster](https://dagster.io/) for orchestration and [FastHTML](https://fastht.ml/) + [MonsterUI](https://github.com/AnswerDotAI/MonsterUI) for the dashboard, Anomstack provides a complete solution for metric monitoring and anomaly detection.

## Key Features

- 🔍 **Powerful Anomaly Detection**: Built on [PyOD](https://pyod.readthedocs.io/en/latest/) for robust anomaly detection
- 📊 **Beautiful Dashboard**: Modern UI for visualizing metrics and anomalies
- 🔌 **Multiple Data Sources**: Support for various databases and data platforms
- 🔔 **Flexible Alerting**: Email and Slack notifications with customizable templates
- 🤖 **LLM Agent Integration**: AI-powered anomaly analysis and reporting
- 🛠️ **Easy Deployment**: Multiple deployment options including Docker, Dagster Cloud, and more

## How It Works

1. **Define Your Metrics**: Configure your metrics using SQL queries or Python functions
2. **Automatic Processing**: Anomstack handles ingestion, training, scoring, and alerting
3. **Monitor & Alert**: Get notified when anomalies are detected
4. **Visualize**: Use the dashboard to explore metrics and anomalies

## Supported Data Sources

Anomstack supports a wide range of data sources:

- Python (direct integration)
- BigQuery
- Snowflake
- ClickHouse
- DuckDB
- SQLite
- MotherDuck
- Turso
- Redshift (coming soon)

## Storage Options

Store your trained models and configurations in:

- Local filesystem
- Google Cloud Storage (GCS)
- Amazon S3
- Azure Blob Storage (coming soon)

## Getting Started

Choose your preferred way to get started:

- [Quickstart Guide](quickstart)
- [Docker Deployment](deployment/docker)
- [Dagster Cloud Setup](deployment/dagster-cloud)
- [Local Development](deployment/local)

## Architecture

Anomstack is built with a modular architecture that separates concerns:

- **Ingestion**: Pull data from various sources
- **Processing**: Train models and detect anomalies
- **Alerting**: Send notifications via multiple channels
- **Dashboard**: Visualize metrics and anomalies
- **Storage**: Store models and configurations

## Contributing

We welcome contributions! Check out our [Contributing Guide](https://github.com/andrewm4894/anomstack/blob/main/CONTRIBUTING.md) to get started.

## License

Anomstack is open source and available under the [MIT License](https://github.com/andrewm4894/anomstack/blob/main/LICENSE).
