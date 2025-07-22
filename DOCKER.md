# Docker Documentation

This document provides comprehensive information about the Docker setup for the Anomstack project.

## Overview

Anomstack uses Docker to containerize all components for easy deployment and development. The setup includes:

- **Dagster Code Server**: Runs your data pipelines
- **Dagster UI (Dagit)**: Web interface for pipeline management
- **Dagster Daemon**: Background process for scheduling and execution
- **Dashboard**: FastHTML-based metrics dashboard
- **PostgreSQL**: Database for Dagster metadata
- **DuckDB Volume**: Persistent storage for metrics data

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

### 1. PostgreSQL Database (`anomstack_postgresql`)
- **Image**: `postgres:11`
- **Purpose**: Stores Dagster run history, schedules, and metadata
- **Port**: 5432 (configurable via `ANOMSTACK_POSTGRES_FORWARD_PORT`)
- **Environment Variables**:
  - `ANOMSTACK_POSTGRES_USER` (default: postgres_user)
  - `ANOMSTACK_POSTGRES_PASSWORD` (default: postgres_password)
  - `ANOMSTACK_POSTGRES_DB` (default: postgres_db)

### 2. Code Server (`anomstack_code`)
- **Image**: `andrewm4894/anomstack_code:latest`
- **Purpose**: Runs Dagster user code via gRPC
- **Port**: 4000 (internal)
- **Restart Policy**: `always`
- **Volumes**:
  - `./tmp:/opt/dagster/app/tmp` (temporary files)
  - `anomstack_metrics_duckdb:/data` (DuckDB data)

### 3. Dagster UI (`anomstack_dagit`)
- **Image**: `andrewm4894/anomstack_dagster:latest`
- **Purpose**: Web interface for pipeline management
- **Port**: 3000 (external)
- **Restart Policy**: `on-failure`
- **Access**: http://localhost:3000

### 4. Dagster Daemon (`anomstack_daemon`)
- **Image**: `andrewm4894/anomstack_dagster:latest`
- **Purpose**: Background process for scheduling and run execution
- **Restart Policy**: `on-failure`
- **Volumes**: Same as dagit (for Docker socket access)

### 5. Dashboard (`anomstack_dashboard`)
- **Image**: `andrewm4894/anomstack_dashboard:latest`
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
- **`/var/run/docker.sock`**: Docker socket for container management
- **`/tmp/io_manager_storage`**: Dagster I/O manager storage

## Environment Configuration

### Required Environment Variables
Create a `.env` file based on `.example.env`:

```bash
# Database paths
ANOMSTACK_DUCKDB_PATH=/data/anomstack.db
ANOMSTACK_SQLITE_PATH=tmpdata/anomstack-sqlite.db

# PostgreSQL
ANOMSTACK_POSTGRES_USER=postgres_user
ANOMSTACK_POSTGRES_PASSWORD=postgres_password
ANOMSTACK_POSTGRES_DB=postgres_db
ANOMSTACK_POSTGRES_FORWARD_PORT=5432

# Dagster
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
make docker-tag               # Tag images for Docker Hub
make docker-push              # Push images to Docker Hub
make docker-build-push        # Build, tag, and push in one command
make docker-pull              # Pull latest images from Docker Hub
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

## Docker Hub Images

All images are available on Docker Hub:
- `andrewm4894/anomstack_code:latest`
- `andrewm4894/anomstack_dagster:latest`
- `andrewm4894/anomstack_dashboard:latest`

### Building and Pushing
Images are automatically tagged and pushed using the Makefile:
```bash
make docker-build-push
```

This ensures consistent deployments across environments.
