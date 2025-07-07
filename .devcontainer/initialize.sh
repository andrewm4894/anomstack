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

# Any other pre-container setup can go here
# For example:
# - Download required files
# - Set up configuration
# - Prepare volumes/directories

echo "Initialize script completed successfully!" 