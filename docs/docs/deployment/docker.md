---
sidebar_position: 1
---

# Docker Deployment

Deploy Anomstack using Docker for easy setup and management.

## Prerequisites

- Docker
- Docker Compose
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/andrewm4894/anomstack.git
cd anomstack
```

2. Start the containers:
```bash
docker compose up -d
```

## Configuration

Configure your Docker deployment through:
- Environment variables
- Volume mounts
- Network settings
- Resource limits

## Examples

Coming soon...

## Best Practices

### Storage Management

Dagster can accumulate significant storage over time. To prevent disk space issues:

- **Monitor storage regularly**: Use `make dagster-cleanup-status`
- **Configure retention policies**: Ensure your `dagster_docker.yaml` has appropriate cleanup settings
- **Schedule regular cleanup**: Run weekly/monthly cleanup jobs

For detailed guidance, see the [Storage Optimization](../storage-optimization.md) guide. 