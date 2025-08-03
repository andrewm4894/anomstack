# Docker Documentation

This document provides comprehensive information about the Docker setup for the Anomstack project.

## Overview

Anomstack uses a **simplified Docker architecture** with local image building and SQLite storage for easy deployment and development. The setup includes:

- **Dagster Code Server**: Runs your data pipelines
- **Dagster UI**: Web interface for pipeline management  
- **Dagster Daemon**: Background process for scheduling and execution (uses DefaultRunLauncher)
- **Dashboard**: FastHTML-based metrics dashboard
- **SQLite Storage**: All Dagster metadata stored in SQLite files (no separate database)
- **DuckDB Volume**: Persistent storage for metrics data

### Key Simplifications
- ✅ **No PostgreSQL**: Uses SQLite for simpler deployment
- ✅ **No Docker Socket**: DefaultRunLauncher runs jobs in same container
- ✅ **Local Builds**: All images built locally (no Docker Hub dependency)
- ✅ **Fewer Resources**: Reduced memory and complexity

## Quick Start

```bash
# Start all services
make docker

# Access services
# - Dagster UI: http://localhost:3000
# - Dashboard: http://localhost:5001
# - PostgreSQL: localhost:5432 (if port forwarding enabled)
```

## Services

### 1. Code Server (`anomstack_code`)
- **Image**: Built locally from `docker/Dockerfile.anomstack_code`
- **Purpose**: Runs Dagster user code via gRPC
- **Port**: 4000 (internal)
- **Restart Policy**: `always`
- **Volumes**:
  - `./tmp:/opt/dagster/app/tmp` (temporary files)
  - `anomstack_metrics_duckdb:/data` (DuckDB data)
  - `./dagster_home:/opt/dagster/dagster_home` (Dagster storage - includes SQLite)

### 2. Dagster UI (`anomstack_webserver`)
- **Image**: Built locally from `docker/Dockerfile.dagster`
- **Purpose**: Web interface for pipeline management  
- **Port**: 3000 (external)
- **Restart Policy**: `on-failure`
- **Access**: http://localhost:3000
- **Storage**: Uses SQLite files in mounted dagster_home volume

### 3. Dagster Daemon (`anomstack_daemon`) 
- **Image**: Built locally from `docker/Dockerfile.dagster`
- **Purpose**: Background process for scheduling and run execution
- **Restart Policy**: `on-failure`
- **Run Launcher**: DefaultRunLauncher (runs jobs in same container process)

### 4. Dashboard (`anomstack_dashboard`)
- **Image**: Built locally from `docker/Dockerfile.anomstack_dashboard`
- **Purpose**: FastHTML-based metrics dashboard
- **Port**: 5001 (external) → 8080 (internal)
- **Restart Policy**: `on-failure`
- **Command**: `uvicorn dashboard.app:app --host 0.0.0.0 --port 8080 --reload`
- **Access**: http://localhost:5001

## Volumes

### Named Volumes
- **`anomstack_metrics_duckdb`**: Persistent storage for DuckDB metrics database
  - **Mount Point**: `/data/`
  - **Purpose**: Stores time-series metrics data
  - **Persistence**: Data survives container restarts

### Bind Mounts
- **`./tmp`**: Temporary files and local artifacts
- **`./dagster_home`**: Dagster configuration, SQLite storage, and logs  
- **`./metrics`**: Hot-reloadable metric configurations

### Storage Simplification
- **SQLite Storage**: All Dagster metadata (runs, schedules, events) stored in SQLite files
- **No PostgreSQL**: Eliminated separate database container for simpler deployment
- **No Docker Socket**: DefaultRunLauncher removes need for Docker socket access

## Environment Configuration

### Required Environment Variables
Create a `.env` file based on `.example.env`:

```bash
# Database paths
ANOMSTACK_DUCKDB_PATH=/data/anomstack.db

# Dagster (uses SQLite for metadata storage)
DAGSTER_HOME=
DAGSTER_LOG_LEVEL=DEBUG
DAGSTER_CONCURRENCY=4

# Dashboard
ANOMSTACK_DASHBOARD_PORT=5001
```

## Makefile Commands

### Basic Operations
```bash
make docker                    # Start all services
make docker-stop              # Stop all services
make docker-rm                # Remove containers and networks
make docker-prune             # Remove everything including volumes (⚠️ deletes data)
```

### Image Management
```bash
make docker-build             # Build all images locally
make docker-smart             # Build and start services (recommended)
```

### Debugging
```bash
make docker-logs              # View all container logs
make docker-logs-code         # View code server logs
make docker-logs-dagit        # View Dagster UI logs
make docker-logs-daemon       # View daemon logs
make docker-logs-dashboard    # View dashboard logs
```

### Shell Access
```bash
make docker-shell-code        # Shell into code server
make docker-shell-dagit       # Shell into Dagster UI container
make docker-shell-dashboard   # Shell into dashboard container
```

### Service Management
```bash
make docker-restart-dashboard # Restart dashboard only
make docker-restart-code      # Restart code server only
```

### Cleanup
```bash
make docker-clean             # Clean up unused Docker resources
```

## Development Workflow

### 1. Initial Setup
```bash
# Copy environment file
cp .example.env .env

# Edit .env with your configuration
# Start services
make docker
```

### 2. Making Changes
```bash
# Make code changes
# Rebuild and push updated images
make docker-build-push

# Restart services to use new images
make docker-stop
make docker
```

### 3. Debugging Issues
```bash
# Check container status
docker compose ps

# View logs
make docker-logs-[service]

# Shell into container
make docker-shell-[service]

# Restart specific service
make docker-restart-[service]
```

## Data Persistence

### DuckDB Database
- **Location**: `/data/anomstack.db` (inside containers)
- **Volume**: `anomstack_metrics_duckdb`
- **Backup**: Use `docker volume` commands to backup

```bash
# Create backup
docker run --rm -v anomstack_metrics_duckdb:/data -v $(pwd):/backup alpine tar czf /backup/duckdb-backup.tar.gz /data

# Restore backup
docker run --rm -v anomstack_metrics_duckdb:/data -v $(pwd):/backup alpine tar xzf /backup/duckdb-backup.tar.gz -C /
```

### PostgreSQL Database
- **Backup**: Use standard PostgreSQL backup tools
- **Data**: Stored in Docker volume (not explicitly named)

## Networking

All services run on the `anomstack_network` bridge network:
- **Internal communication**: Services can reach each other by container name
- **External access**: Only specific ports are exposed to host

### Port Mapping
- **3000**: Dagster UI
- **5001**: Dashboard
- **5432**: PostgreSQL (if enabled)

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
make docker-logs-[service]

# Check container status
docker compose ps

# Restart service
make docker-restart-[service]
```

#### 2. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :3000

# Stop conflicting service or change port in docker-compose.yaml
```

#### 3. Volume Issues
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect anomstack_metrics_duckdb

# Remove volume (⚠️ deletes data)
docker volume rm anomstack_metrics_duckdb
```

#### 4. Image Issues
```bash
# Pull latest images
make docker-pull

# Rebuild images
make docker-build-push

# Clean up old images
make docker-clean
```

### Service-Specific Issues

#### Dashboard Not Loading
- Check if using uvicorn command (not direct Python)
- Verify FastHTML dependencies are installed
- Check for port conflicts (5001)

#### Dagster UI Not Accessible
- Verify dagit container is running
- Check if code server is accessible
- Review workspace.yaml configuration

#### Code Server Issues
- Check if all dependencies are installed
- Verify environment variables are set
- Check DuckDB volume mount

## Production Considerations

### Security
- Use secrets management for sensitive environment variables
- Limit network exposure
- Use specific image tags instead of `latest`

### Performance
- Adjust resource limits in docker-compose.yaml
- Monitor container resource usage
- Use external databases for production

### Monitoring
- Implement health checks
- Set up log aggregation
- Monitor volume usage

## Building Images

All images are built locally from their respective Dockerfiles:
- `anomstack_code_image` - Built from `docker/Dockerfile.anomstack_code`
- `anomstack_dagster_image` - Built from `docker/Dockerfile.dagster`  
- `anomstack_dashboard_image` - Built from `docker/Dockerfile.anomstack_dashboard`

### Building Images
Images are built automatically when using Docker Compose:
```bash
# Build and start all services
make docker-smart

# Or build manually
docker compose build --no-cache
```

This ensures you're always running the latest code and dependencies.
