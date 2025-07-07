#!/usr/bin/env bash

set -ex

echo "start post create command..."

# install requirements-dev.txt
pip install -r requirements-dev.txt

# install pre-commit
pre-commit install

# Wait a moment for services to start
sleep 5

# Check service status
echo "Checking service status..."
docker compose ps

# Create tmp directory for local development
mkdir -p tmp

# Set permissions for tmp directory
chmod 777 tmp

# Create dagster_home directory
mkdir -p /opt/dagster/dagster_home

# Set permissions for dagster_home directory
chmod 777 /opt/dagster/dagster_home

echo "Setup complete!"
echo "Services:"
echo "- Dagit (Dagster UI): http://localhost:3000"
echo "- Dashboard: http://localhost:5001"
echo "- PostgreSQL: localhost:5432"
echo ""
echo "To start working:"
echo "- All services should be running automatically"
echo "- Check 'docker compose ps' to verify"
echo "- Use 'make local' to run Dagster locally if needed"
echo ""
echo "done post create command"
