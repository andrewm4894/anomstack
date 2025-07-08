#!/usr/bin/env bash

set -ex

echo "start post create command..."

# Change to the workspace directory
cd /opt/dagster/app

# install requirements-dev.txt if it exists
if [ -f requirements-dev.txt ]; then
    echo "Installing requirements-dev.txt..."
    pip install -r requirements-dev.txt
else
    echo "requirements-dev.txt not found, skipping..."
fi

# install pre-commit if available
if command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit hooks..."
    pre-commit install || echo "pre-commit install failed, continuing..."
else
    echo "pre-commit not available, skipping..."
fi

# Wait a moment for services to start
sleep 5

# Check service status (only if docker compose is available)
if command -v docker &> /dev/null; then
    echo "Checking service status..."
    docker compose ps || echo "Docker compose not available or services not running"
else
    echo "Docker not available in container, skipping service check"
fi

# Create tmp directory for local development
mkdir -p /opt/dagster/app/tmp

# Set permissions for tmp directory
chmod 777 /opt/dagster/app/tmp

# Create dagster_home directory
mkdir -p /opt/dagster/dagster_home

# Set permissions for dagster_home directory
chmod 777 /opt/dagster/dagster_home

echo "Setup complete!"
echo "Services:"
echo "- Dagster Webserver: http://localhost:3000"
echo "- Dashboard: http://localhost:5001"
echo "- PostgreSQL: localhost:5432"
echo ""
echo "To start working:"
echo "- All services should be running automatically"
echo "- Check 'docker compose ps' to verify"
echo "- Use 'make local' to run Dagster locally if needed"
echo ""
echo "done post create command"
