#!/bin/bash

# Anomstack Render API Deployment Script
# Creates a new web service on Render using the API
# Usage: ./deploy_render_api.sh [--profile demo|production|development]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default configuration
PROFILE="demo"
SERVICE_NAME="anomstack-demo"
REGION="oregon"
PLAN="starter"
DISK_SIZE_GB=10
GITHUB_REPO="https://github.com/andrewm4894/anomstack"
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile) PROFILE="$2"; shift 2 ;;
        --service-name) SERVICE_NAME="$2"; shift 2 ;;
        --region) REGION="$2"; shift 2 ;;
        --plan) PLAN="$2"; shift 2 ;;
        --yes|-y) CONFIRM=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Anomstack Render API Deployment             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Service Name: $SERVICE_NAME"
echo "  Profile:      $PROFILE"
echo "  Branch:       $BRANCH"
echo "  Region:       $REGION"
echo "  Plan:         $PLAN"
echo "  Disk Size:    ${DISK_SIZE_GB}GB"
echo ""

# Check for API key
if [ -z "$RENDER_API_KEY" ]; then
    echo -e "${RED}❌ Error: RENDER_API_KEY not set${NC}"
    echo ""
    echo "Get your API key:"
    echo "  1. Go to: https://dashboard.render.com/u/settings#api-keys"
    echo "  2. Click 'Create API Key'"
    echo "  3. Export it: export RENDER_API_KEY='rnd_xxx...'"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Render API key found${NC}"

# Get owner ID from API
echo -e "${BLUE}🔍 Fetching account information...${NC}"
OWNER_RESPONSE=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Accept: application/json" \
    "https://api.render.com/v1/owners")

OWNER_ID=$(echo "$OWNER_RESPONSE" | jq -r '.[0].owner.id' 2>/dev/null)

if [ -z "$OWNER_ID" ] || [ "$OWNER_ID" = "null" ]; then
    echo -e "${RED}❌ Failed to get owner ID${NC}"
    echo "Response: $OWNER_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Owner ID: $OWNER_ID${NC}"

# Check if service already exists
echo -e "${BLUE}🔍 Checking if service '$SERVICE_NAME' already exists...${NC}"
EXISTING_SERVICE=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services" | jq -r ".[] | select(.service.name == \"$SERVICE_NAME\") | .service.id")

if [ -n "$EXISTING_SERVICE" ]; then
    echo -e "${YELLOW}⚠️  Service '$SERVICE_NAME' already exists (ID: $EXISTING_SERVICE)${NC}"
    echo -e "${YELLOW}⚠️  Will update existing service instead of creating new one${NC}"
    SERVICE_ID="$EXISTING_SERVICE"
    UPDATE_MODE=true
else
    echo -e "${GREEN}✅ Service does not exist, will create new service${NC}"
    UPDATE_MODE=false
fi

# Load profile environment variables
PROFILE_FILE="$PROJECT_ROOT/profiles/${PROFILE}.env"
if [ ! -f "$PROFILE_FILE" ]; then
    echo -e "${RED}❌ Profile not found: $PROFILE_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Loading profile: ${PROFILE}.env${NC}"

# Build environment variables JSON array
ENV_VARS='[]'

# Add core variables
add_env_var() {
    local key="$1"
    local value="$2"
    ENV_VARS=$(echo "$ENV_VARS" | jq --arg k "$key" --arg v "$value" '. += [{"key": $k, "value": $v}]')
}

# Core Dagster configuration
add_env_var "DAGSTER_HOME" "/opt/dagster/dagster_home"
add_env_var "DAGSTER_WEBSERVER_HOST" "0.0.0.0"
add_env_var "DAGSTER_WEBSERVER_PORT" "3000"
add_env_var "DAGSTER_WORKSPACE_FORCE_RELOAD" "true"
add_env_var "ANOMSTACK_DUCKDB_PATH" "/data/anomstack.db"
add_env_var "ANOMSTACK_MODEL_PATH" "local:///data/models"
add_env_var "ANOMSTACK_TABLE_KEY" "metrics"
add_env_var "PYTHONPATH" "/opt/dagster/app"

# Load variables from profile
while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    [[ "$key" =~ ^[[:space:]]*# ]] || [[ -z "$key" ]] && continue

    # Trim whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Skip if empty
    [[ -z "$key" ]] && continue

    # Add to env vars
    add_env_var "$key" "$value"
done < "$PROFILE_FILE"

ENV_VAR_COUNT=$(echo "$ENV_VARS" | jq 'length')
echo -e "${GREEN}✅ Loaded $ENV_VAR_COUNT environment variables${NC}"

# Build API payload
PAYLOAD=$(cat <<EOF
{
  "type": "web_service",
  "name": "$SERVICE_NAME",
  "ownerId": "$OWNER_ID",
  "repo": "$GITHUB_REPO",
  "branch": "$BRANCH",
  "region": "$REGION",
  "plan": "$PLAN",
  "numInstances": 1,
  "autoDeploy": "yes",
  "serviceDetails": {
    "env": "docker",
    "healthCheckPath": "/nginx-health",
    "disk": {
      "name": "anomstack-data",
      "mountPath": "/data",
      "sizeGB": $DISK_SIZE_GB
    },
    "envSpecificDetails": {
      "dockerfilePath": "./docker/Dockerfile.render",
      "dockerContext": ".",
      "dockerCommand": ""
    },
    "envVars": $ENV_VARS
  }
}
EOF
)

echo ""
echo -e "${YELLOW}📦 Service Configuration:${NC}"
echo "$PAYLOAD" | jq '{name, region, plan, dockerfilePath: .serviceDetails.envSpecificDetails.dockerfilePath, disk: .serviceDetails.disk, envVarCount: (.serviceDetails.envVars | length)}'
echo ""

echo -e "${YELLOW}⚠️  This will create a NEW service on Render${NC}"
echo -e "${YELLOW}⚠️  Set ANOMSTACK_ADMIN_PASSWORD as secret after creation${NC}"
echo ""

if [ "$CONFIRM" = false ]; then
    read -p "Press Enter to continue or Ctrl+C to cancel... "
else
    echo "Auto-confirming deployment (--yes flag)"
fi

echo ""

if [ "$UPDATE_MODE" = true ]; then
    echo -e "${BLUE}🔄 Updating existing service...${NC}"

    # Update service via API (PATCH)
    UPDATE_PAYLOAD=$(echo "$PAYLOAD" | jq 'del(.type, .ownerId, .name)')

    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X PATCH "https://api.render.com/v1/services/$SERVICE_ID" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$UPDATE_PAYLOAD")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Service updated successfully!${NC}"
        echo ""

        SERVICE_URL=$(echo "$BODY" | jq -r '.service.serviceDetails.url // .serviceDetails.url // empty' 2>/dev/null)

        echo -e "${GREEN}Service Details:${NC}"
        echo "  Service ID: $SERVICE_ID"
        [ -n "$SERVICE_URL" ] && echo "  URL: https://$SERVICE_URL"
        echo ""

        # Trigger new deploy after update
        echo -e "${BLUE}🚀 Triggering new deployment...${NC}"
        DEPLOY_RESPONSE=$(curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"clearCache": "do_not_clear"}')

        DEPLOY_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.id')
        echo -e "${GREEN}✅ Deploy triggered (ID: $DEPLOY_ID)${NC}"
    else
        echo -e "${RED}❌ Failed to update service (HTTP $HTTP_CODE)${NC}"
        echo ""
        echo "Response:"
        echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
        echo ""
        exit 1
    fi
else
    echo -e "${BLUE}🚀 Creating new service...${NC}"

    # Create service via API
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST "https://api.render.com/v1/services" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$PAYLOAD")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Service created successfully!${NC}"
        echo ""

        SERVICE_ID=$(echo "$BODY" | jq -r '.service.id // .id' 2>/dev/null)
        SERVICE_URL=$(echo "$BODY" | jq -r '.service.serviceDetails.url // .serviceDetails.url // empty' 2>/dev/null)

        echo -e "${GREEN}Service Details:${NC}"
        echo "  Service ID: $SERVICE_ID"
        [ -n "$SERVICE_URL" ] && echo "  URL: https://$SERVICE_URL"
        echo ""

        # Trigger initial deploy
        echo -e "${BLUE}🚀 Triggering initial deployment...${NC}"
        DEPLOY_RESPONSE=$(curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"clearCache": "do_not_clear"}')

        DEPLOY_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.id')
        echo -e "${GREEN}✅ Deploy triggered (ID: $DEPLOY_ID)${NC}"
    else
        echo -e "${RED}❌ Failed to create service (HTTP $HTTP_CODE)${NC}"
        echo ""
        echo "Response:"
        echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
        echo ""
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  1. View deployment: https://dashboard.render.com/web/$SERVICE_ID"
echo "  2. Set ANOMSTACK_ADMIN_PASSWORD secret (if not already set):"
echo "     - Go to service → Environment"
echo "     - Mark ANOMSTACK_ADMIN_PASSWORD as secret"
echo "     - Set your admin password"
echo "  3. Wait for build to complete (~5-10 minutes)"
echo "  4. Access dashboard: https://anomstack-demo.onrender.com"
echo ""

echo -e "${BLUE}💡 View logs:${NC}"
echo "  export RENDER_SERVICE_ID=$SERVICE_ID"
echo "  make render-logs"
echo ""

echo -e "${GREEN}✅ Deployment initiated successfully!${NC}"
