# Docker Documentation

This document provides comprehensive information about the Docker setup for the Anomstack project.

## Overview

Anomstack uses a **simplified 3-container Docker architecture** with direct Python module loading and SQLite storage for improved reliability and easy deployment. The setup includes:

- **Dagster Webserver + User Code** (consolidated): Web interface and data pipelines in a single container using direct Python module loading
- **Dagster Daemon**: Background process for scheduling and execution (uses DefaultRunLauncher)
- **Dashboard**: FastHTML-based metrics dashboard
- **SQLite Storage**: All Dagster metadata stored in SQLite files (no separate database)
- **DuckDB Volume**: Persistent storage for metrics data

### Key Simplifications
- ✅ **No gRPC Code Server**: User code loaded directly as Python module (eliminates network overhead and reliability issues)
- ✅ **No PostgreSQL**: Uses SQLite for simpler deployment
- ✅ **No Docker Socket**: DefaultRunLauncher runs jobs in same container
- ✅ **Local Builds**: All images built locally (no Docker Hub dependency)
- ✅ **Fewer Resources**: Reduced memory and complexity with consolidated architecture

## Quick Start

```bash
# Start all services
make docker

# Access services
# - Dagster UI: http://localhost:3000 (with embedded user code)
# - Dashboard: http://localhost:5001
```

## Services

### 1. Dagster Webserver + User Code (`anomstack_webserver`)
- **Image**: Built locally from `docker/Dockerfile.dagster_consolidated`
- **Purpose**: Web interface and user code execution using direct Python module loading (no gRPC server needed)
- **Port**: 3000 (external)
- **Restart Policy**: `on-failure`
- **Access**: http://localhost:3000
- **Storage**: Uses SQLite files in mounted dagster_home volume
- **Volumes**:
  - `./tmp:/opt/dagster/app/tmp` (temporary files)
  - `anomstack_metrics_duckdb:/data` (DuckDB data)
  - `./dagster_home:/opt/dagster/dagster_home` (Dagster storage - includes SQLite)

### 2. Dagster Daemon (`anomstack_daemon`) 
- **Image**: Built locally from `docker/Dockerfile.dagster_consolidated`
- **Purpose**: Background process for scheduling and run execution
- **Restart Policy**: `on-failure`
- **Run Launcher**: DefaultRunLauncher (runs jobs in same container process)

### 3. Dashboard (`anomstack_dashboard`)
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
make docker-logs-webserver    # View consolidated webserver logs (with embedded user code)
make docker-logs-daemon       # View daemon logs
make docker-logs-dashboard    # View dashboard logs
```

### Shell Access
```bash
make docker-shell-webserver   # Shell into consolidated webserver container
make docker-shell-daemon      # Shell into daemon container
make docker-shell-dashboard   # Shell into dashboard container
```

### Service Management
```bash
make docker-restart-dashboard # Restart dashboard only
make docker-restart-webserver # Restart webserver (with embedded user code) only
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


## Networking

All services run on the `anomstack_network` bridge network:
- **Internal communication**: Services can reach each other by container name
- **External access**: Only specific ports are exposed to host

### Port Mapping
- **3000**: Dagster UI (with embedded user code)
- **5001**: Dashboard

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
- Verify webserver container is running (now includes embedded user code)
- Review workspace.yaml configuration for direct Python module loading
- Check if user code is properly embedded in consolidated container

#### User Code Issues
- Check if all dependencies are installed in consolidated container
- Verify environment variables are set
- Check DuckDB volume mount
- Ensure Python module loading is working (no gRPC server needed)

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
- `anomstack_consolidated_image` - Built from `docker/Dockerfile.dagster_consolidated` (includes both webserver and user code)
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
