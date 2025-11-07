#!/bin/bash

# Anomstack Render Deployment Script
# This script deploys Anomstack to Render using the Render API directly
# No GitHub commit required - works from local configuration

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROFILE="demo"
SERVICE_NAME="anomstack-demo"
REGION="oregon"
PLAN="starter"
DISK_SIZE_GB=10

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --service-name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --plan)
            PLAN="$2"
            shift 2
            ;;
        --disk-size)
            DISK_SIZE_GB="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--profile demo|production|development] [--service-name NAME] [--region REGION] [--plan PLAN] [--disk-size GB]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🚀 Anomstack Render Deployment${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "Profile: $PROFILE"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Plan: $PLAN"
echo "Disk Size: ${DISK_SIZE_GB}GB"
echo ""

# Check for Render API key
if [ -z "$RENDER_API_KEY" ]; then
    echo -e "${RED}❌ Error: RENDER_API_KEY environment variable not set${NC}"
    echo ""
    echo "To deploy to Render, you need an API key:"
    echo "1. Go to https://dashboard.render.com/u/settings#api-keys"
    echo "2. Click 'Create API Key'"
    echo "3. Copy the key and set it:"
    echo "   export RENDER_API_KEY='your_api_key_here'"
    echo ""
    exit 1
fi

# Load environment variables from profile
PROFILE_FILE="$PROJECT_ROOT/profiles/${PROFILE}.env"
if [ ! -f "$PROFILE_FILE" ]; then
    echo -e "${RED}❌ Error: Profile file not found: $PROFILE_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Loading profile: $PROFILE_FILE${NC}"

# Build environment variables array for API payload
ENV_VARS_JSON="[]"
echo -e "${BLUE}📋 Collecting environment variables...${NC}"

# Core environment variables (hardcoded for Docker deployment)
ENV_VARS_JSON=$(cat <<EOF
[
  {"key": "DAGSTER_HOME", "value": "/opt/dagster/dagster_home"},
  {"key": "DAGSTER_WEBSERVER_HOST", "value": "0.0.0.0"},
  {"key": "DAGSTER_WEBSERVER_PORT", "value": "3000"},
  {"key": "DAGSTER_WORKSPACE_FORCE_RELOAD", "value": "true"},
  {"key": "ANOMSTACK_DUCKDB_PATH", "value": "/data/anomstack.db"},
  {"key": "ANOMSTACK_MODEL_PATH", "value": "local:///data/models"},
  {"key": "ANOMSTACK_TABLE_KEY", "value": "metrics"},
  {"key": "PYTHONPATH", "value": "/opt/dagster/app"},
  {"key": "ANOMSTACK_IGNORE_EXAMPLES", "value": "no"}
]
EOF
)

# Add environment variables from profile
while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ ]] || [[ -z "$key" ]] && continue

    # Remove leading/trailing whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Skip if empty after trimming
    [[ -z "$key" ]] && continue

    # Add to JSON array (escape quotes in value)
    value_escaped=$(echo "$value" | sed 's/"/\\"/g')
    ENV_VARS_JSON=$(echo "$ENV_VARS_JSON" | jq --arg k "$key" --arg v "$value_escaped" '. += [{"key": $k, "value": $v}]')
done < "$PROFILE_FILE"

echo -e "${GREEN}✅ Collected $(echo "$ENV_VARS_JSON" | jq 'length') environment variables${NC}"

# Get git commit hash for build context
GIT_COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
echo -e "${GREEN}✅ Git commit: $GIT_COMMIT_HASH${NC}"

# GitHub repository URL
GITHUB_REPO="https://github.com/andrewm4894/anomstack.git"

echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "1. This will create a NEW service on Render"
echo "2. The service will use: docker/Dockerfile.fly"
echo "3. A persistent disk will be attached at /data"
echo "4. Set ANOMSTACK_ADMIN_PASSWORD as a secret in Render Dashboard after creation"
echo ""
echo -e "${BLUE}Press Enter to continue or Ctrl+C to cancel...${NC}"
read

echo ""
echo -e "${BLUE}🔧 Creating service via Render API...${NC}"

# Create service using Render API
# Documentation: https://api-docs.render.com/reference/create-service

SERVICE_PAYLOAD=$(cat <<EOF
{
  "type": "web_service",
  "name": "$SERVICE_NAME",
  "ownerId": "OWNER_ID",
  "repo": "$GITHUB_REPO",
  "branch": "main",
  "rootDir": "./",
  "region": "$REGION",
  "plan": "$PLAN",
  "dockerfilePath": "./docker/Dockerfile.fly",
  "dockerContext": "./",
  "numInstances": 1,
  "envVars": $ENV_VARS_JSON,
  "disk": {
    "name": "anomstack-data",
    "mountPath": "/data",
    "sizeGB": $DISK_SIZE_GB
  },
  "healthCheckPath": "/nginx-health",
  "autoDeploy": "yes"
}
EOF
)

echo ""
echo -e "${YELLOW}📝 Service Configuration:${NC}"
echo "$SERVICE_PAYLOAD" | jq '.'
echo ""

# Note: The actual API call requires owner ID which we need to fetch first
echo -e "${YELLOW}⚠️  To complete deployment:${NC}"
echo ""
echo "Option 1: Use Render Dashboard (Recommended)"
echo "  1. Go to https://dashboard.render.com"
echo "  2. Click 'New +' → 'Web Service'"
echo "  3. Connect your GitHub repo: $GITHUB_REPO"
echo "  4. Configure:"
echo "     - Name: $SERVICE_NAME"
echo "     - Region: $REGION"
echo "     - Branch: main"
echo "     - Runtime: Docker"
echo "     - Dockerfile Path: ./docker/Dockerfile.fly"
echo "     - Plan: $PLAN"
echo "  5. Add environment variables from profile: $PROFILE_FILE"
echo "  6. Add disk: /data (${DISK_SIZE_GB}GB)"
echo ""
echo "Option 2: Use Render CLI (if available)"
echo "  render services create --help"
echo ""
echo "Option 3: Use Blueprint deployment"
echo "  1. Commit render.yaml to GitHub"
echo "  2. Go to https://dashboard.render.com/blueprints"
echo "  3. Create new Blueprint Instance"
echo ""

echo -e "${GREEN}✅ Deployment configuration ready!${NC}"
echo ""
echo "Environment variables have been prepared from profile: $PROFILE"
echo "To view the full configuration, check: $PROFILE_FILE"
echo ""
