#!/bin/bash

# Anomstack Fly.io Configuration Validation Script
set -e

echo "🔍 Validating Anomstack Fly.io deployment configuration..."

# Check if required files exist
REQUIRED_FILES=(
    "fly.toml"
    "docker/Dockerfile.fly"
    "dagster_fly.yaml"

    "scripts/deployment/deploy_fly.sh"
)

echo "📁 Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
        exit 1
    fi
done

# Validate fly.toml syntax
echo "📋 Validating fly.toml syntax..."
if fly config validate; then
    echo "✅ fly.toml is valid"
else
    echo "❌ fly.toml has syntax errors"
    exit 1
fi

# Check if fly CLI is available and user is logged in
echo "🔐 Checking Fly.io CLI authentication..."
if fly auth whoami &>/dev/null; then
    FLY_USER=$(fly auth whoami)
    echo "✅ Logged into Fly.io as: $FLY_USER"
else
    echo "❌ Not logged into Fly.io. Run 'fly auth login' first."
    exit 1
fi

# Validate Dockerfile
echo "🐳 Checking Docker configuration..."
if [[ -f "docker/Dockerfile.fly" ]]; then
    echo "✅ Dockerfile.fly exists"
    # Basic syntax check
    if grep -q "FROM python:3.12-slim" docker/Dockerfile.fly; then
        echo "✅ Dockerfile uses correct base image"
    else
        echo "⚠️  Warning: Dockerfile may not use expected base image"
    fi
else
    echo "❌ Dockerfile.fly not found"
    exit 1
fi

# Check Dagster configuration
echo "⚙️  Checking Dagster configuration..."
if [[ -f "dagster_fly.yaml" ]]; then
    if grep -q "DefaultRunLauncher" dagster_fly.yaml; then
        echo "✅ Using DefaultRunLauncher (Docker-free)"
    else
        echo "❌ Not using DefaultRunLauncher - this won't work on Fly.io"
        exit 1
    fi
else
    echo "❌ dagster_fly.yaml not found"
    exit 1
fi

# Check workspace configuration
echo "📋 Checking workspace configuration..."
if [[ -f "dagster_home/workspace.yaml" ]]; then
    if grep -q "DAGSTER_CODE_SERVER_HOST" dagster_home/workspace.yaml; then
        echo "✅ Workspace configured with environment variable substitution"
    else
        echo "❌ Workspace should use DAGSTER_CODE_SERVER_HOST environment variable"
        exit 1
    fi
else
    echo "❌ workspace.yaml not found"
    exit 1
fi

# Check requirements files
echo "📦 Checking Python requirements..."
REQUIREMENTS_FILES=("requirements.txt" "requirements-dashboard.txt")
for req_file in "${REQUIREMENTS_FILES[@]}"; do
    if [[ -f "$req_file" ]]; then
        echo "✅ $req_file exists"
    else
        echo "❌ $req_file is missing"
        exit 1
    fi
done

echo ""
echo "🎉 All validation checks passed!"
echo ""
echo "Your Anomstack is ready for Fly.io deployment!"
echo ""
echo "Next steps:"
echo "  1. Run './scripts/deployment/deploy_fly.sh' to deploy"
echo "  2. Or run './scripts/deployment/deploy_fly.sh my-custom-name' for custom app name"
echo ""
echo "Estimated deployment time: 5-10 minutes"
echo "Estimated monthly cost: \$15-25 (for light usage)" 