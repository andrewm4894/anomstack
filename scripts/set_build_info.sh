#!/bin/bash

# Set build information environment variables for Docker builds

# Get current git commit hash
HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Get current timestamp 
TIME=$(date -u "+%Y-%m-%d %H:%M:%S UTC")

# Export for use in docker-compose or other scripts
export ANOMSTACK_BUILD_HASH="$HASH"
export ANOMSTACK_BUILD_TIME="$TIME"

echo "Build info set:"
echo "  ANOMSTACK_BUILD_HASH=$ANOMSTACK_BUILD_HASH"
echo "  ANOMSTACK_BUILD_TIME=$ANOMSTACK_BUILD_TIME"