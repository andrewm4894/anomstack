# Docker Setup

This directory contains Dockerfiles for the Anomstack project components.

## Dockerfiles

### `Dockerfile.anomstack_code`
- **Purpose**: Runs the Dagster user code server
- **Image**: `andrewm4894/anomstack_code:latest`
- **Port**: 4000 (internal gRPC)

### `Dockerfile.dagster`
- **Purpose**: Runs Dagster UI (dagit) and daemon
- **Image**: `andrewm4894/anomstack_dagster:latest`
- **Port**: 3000 (dagit UI)

### `Dockerfile.anomstack_dashboard`
- **Purpose**: Runs the FastHTML dashboard
- **Image**: `andrewm4894/anomstack_dashboard:latest`
- **Port**: 8080 (internal), 5001 (external)

## Building Images

### Build All Images
```bash
make docker-build
```

### Build Individual Images
```bash
# Code server
docker build -f docker/Dockerfile.anomstack_code -t anomstack_code_image .

# Dagster services
docker build -f docker/Dockerfile.dagster -t anomstack_dagster_image .

# Dashboard
docker build -f docker/Dockerfile.anomstack_dashboard -t anomstack_dashboard_image .
```

## Running Services

### Using Docker Compose (Recommended)
```bash
# Start all services
make docker

# Stop all services
make docker-stop

# View logs
make docker-logs
```

### Manual Container Run (Not Recommended)
```bash
# Dashboard only
docker run -p 5001:8080 --env-file .env anomstack_dashboard_image
```

## Notes

- All images are built and pushed to Docker Hub for faster deployment
- Use `make docker-build-push` to build and push updated images
- The dashboard uses uvicorn with FastHTML, not direct Python execution
- See `../DOCKER.md` for comprehensive Docker documentation

```bash
docker build -t anomstack-dashboard -f docker/Dockerfile.anomstack_dashboard .
```
