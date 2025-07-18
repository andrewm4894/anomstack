#!/usr/bin/env bash

set -ex

echo "Running initialize script (pre-container setup)..."

# Copy .example.env to .env if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .example.env"
    cp .example.env .env
else
    echo ".env already exists, skipping copy"
fi

# Create tmp directory if it doesn't exist
mkdir -p tmp

# Create dagster_home directory at the same path used by Docker Compose
mkdir -p /opt/dagster/dagster_home

# Set python_ingest_simple example jobs to RUNNING for GitHub Codespaces
PYTHON_INGEST_CONFIG="metrics/examples/python/python_ingest_simple/python_ingest_simple.yaml"
if [ -f "$PYTHON_INGEST_CONFIG" ]; then
    echo "Updating python_ingest_simple job schedules to RUNNING for Codespaces..."
    
    # Array of schedule statuses to set to RUNNING
    SCHEDULE_STATUSES=(
        "ingest_default_schedule_status"
        "train_default_schedule_status"
        "score_default_schedule_status"
        "alert_default_schedule_status"
    )
    
    # Update each schedule status
    for status in "${SCHEDULE_STATUSES[@]}"; do
        if grep -q "$status:" "$PYTHON_INGEST_CONFIG"; then
            # Replace existing line
            sed -i "s/${status}:.*/${status}: \"RUNNING\"/" "$PYTHON_INGEST_CONFIG"
            echo "Updated existing $status to RUNNING"
        else
            # Add new line after metric_batch line
            sed -i "/^metric_batch:/a ${status}: \"RUNNING\"" "$PYTHON_INGEST_CONFIG"
            echo "Added $status: RUNNING"
        fi
    done
    
    echo "Updated python_ingest_simple job schedules to RUNNING"
else
    echo "Warning: python_ingest_simple.yaml not found at $PYTHON_INGEST_CONFIG"
fi

# Any other pre-container setup can go here
# For example:
# - Download required files
# - Set up configuration
# - Prepare volumes/directories

echo "Initialize script completed successfully!" 