#!/bin/bash

# Anomstack Fly.io Deployment Script
set -e

echo "🚀 Deploying Anomstack to Fly.io..."

# Check if fly CLI is installed and user is logged in
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI is not installed. Please install it first:"
    echo "   https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

if ! fly auth whoami &> /dev/null; then
    echo "❌ You are not logged into Fly.io. Please run 'fly auth login' first."
    exit 1
fi

echo "✅ Fly CLI is installed and you are logged in."

# Set app name (can be customized)
APP_NAME="${1:-anomstack-demo}"
echo "📱 App name: $APP_NAME"



# Create Fly.io app if it doesn't exist
echo "🏗️  Creating Fly.io app (or using existing)..."
if ! fly apps list | grep -q "$APP_NAME"; then
    fly apps create "$APP_NAME" --generate-name
else
    echo "✅ App $APP_NAME already exists"
fi

# Create persistent volume for data storage
echo "💾 Setting up persistent volume..."
if ! fly volumes list -a "$APP_NAME" | grep -q "anomstack_data"; then
    fly volumes create anomstack_data --region ord --size 10 -a "$APP_NAME"
    echo "✅ Created 10GB persistent volume"
else
    echo "✅ Volume anomstack_data already exists"
fi

# Create Postgres database
echo "🗄️  Setting up PostgreSQL database..."
if ! fly postgres list | grep -q "$APP_NAME-db"; then
    echo "Creating new Postgres cluster..."
    fly postgres create --name "$APP_NAME-db" --region ord --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 10
    echo "✅ PostgreSQL database created"
else
    echo "✅ PostgreSQL database already exists"
fi

# Attach the database to the app
echo "🔗 Attaching database to app..."
fly postgres attach "$APP_NAME-db" -a "$APP_NAME" || echo "Database may already be attached"

echo "⚙️  Setting environment variables..."

# Collect all environment variables in a single array to minimize releases
declare -a all_secrets=()

# Always set these container-specific paths (these must be correct for the container)
all_secrets+=("DAGSTER_HOME=/opt/dagster/dagster_home")
all_secrets+=("PYTHONPATH=/opt/dagster/app")

# Set Fly.io defaults only if not already defined in .env
if ! grep -q "^DAGSTER_CODE_SERVER_HOST=" ".env" 2>/dev/null; then
    all_secrets+=("DAGSTER_CODE_SERVER_HOST=localhost")
fi

if ! grep -q "^ANOMSTACK_DUCKDB_PATH=" ".env" 2>/dev/null; then
    all_secrets+=("ANOMSTACK_DUCKDB_PATH=/data/anomstack.db")
fi

if ! grep -q "^ANOMSTACK_MODEL_PATH=" ".env" 2>/dev/null; then
    all_secrets+=("ANOMSTACK_MODEL_PATH=local:///data/models")
fi

if ! grep -q "^ANOMSTACK_TABLE_KEY=" ".env" 2>/dev/null; then
    all_secrets+=("ANOMSTACK_TABLE_KEY=metrics")
fi

if ! grep -q "^ANOMSTACK_IGNORE_EXAMPLES=" ".env" 2>/dev/null; then
    all_secrets+=("ANOMSTACK_IGNORE_EXAMPLES=no")
fi

# Handle admin credentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD=""

if [[ ! -f ".env" ]] || ! grep -q "ANOMSTACK_ADMIN_PASSWORD=" ".env" 2>/dev/null; then
    echo "🔐 Generating admin credentials (no .env admin password found)..."
    ADMIN_PASSWORD="$(openssl rand -base64 12)"
    all_secrets+=("ANOMSTACK_ADMIN_USERNAME=$ADMIN_USERNAME")
    all_secrets+=("ANOMSTACK_ADMIN_PASSWORD=$ADMIN_PASSWORD")
    echo "🔑 Generated admin credentials:"
    echo "  Username: $ADMIN_USERNAME"
    echo "  Password: $ADMIN_PASSWORD"
    echo "  (Save these credentials securely!)"
else
    # Get credentials from .env
    ADMIN_USERNAME=$(grep "ANOMSTACK_ADMIN_USERNAME=" ".env" 2>/dev/null | cut -d'=' -f2 | tr -d ' ' || echo "admin")
    ADMIN_PASSWORD=$(grep "ANOMSTACK_ADMIN_PASSWORD=" ".env" 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
    echo "✅ Using admin credentials from .env file"
    echo "🔑 Admin credentials:"
    echo "  Username: $ADMIN_USERNAME"
    echo "  Password: $ADMIN_PASSWORD"
fi

# Add environment variables from .env file
if [[ -f ".env" ]]; then
    echo "📁 Reading environment variables from .env..."
    
    # Variables that should NOT be sent to Fly (local development only)
    skip_patterns=(
        "ANOMSTACK_HOME=\\."              # Current directory
        "ANOMSTACK_POSTGRES_FORWARD_PORT" # Port forwarding is local only
        "DAGSTER_CODE_SERVER_HOST.*anomstack_code" # Docker compose specific
        "ANOMSTACK_DASHBOARD_PORT"        # Local dashboard port
    )
    
    # Read .env file and process each line
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Skip lines that don't contain =
        [[ ! "$line" =~ = ]] && continue
        
        # Extract variable name and value
        var_name=$(echo "$line" | cut -d'=' -f1 | tr -d ' ')
        var_value=$(echo "$line" | cut -d'=' -f2- | tr -d ' ')
        
        # Skip empty values
        [[ -z "$var_value" ]] && continue
        
        # Check if this variable should be skipped (local development only)
        should_skip=false
        for pattern in "${skip_patterns[@]}"; do
            if [[ "$line" =~ $pattern ]]; then
                should_skip=true
                break
            fi
        done
        
        # Add to secrets array if not skipped
        if [[ "$should_skip" == "false" ]]; then
            all_secrets+=("$var_name=$var_value")
        fi
        
    done < ".env"
fi

# Set all secrets in one command to minimize releases
if [[ ${#all_secrets[@]} -gt 0 ]]; then
    echo "🔐 Setting ${#all_secrets[@]} environment variables as Fly secrets in single operation..."
    
    # Set all secrets at once
    fly secrets set "${all_secrets[@]}" -a "$APP_NAME"
    
    echo "✅ All environment variables set successfully!"
else
    echo "⚠️  No environment variables found to set."
fi



# Update fly.toml with correct app name
sed -i.bak "s/app = \".*\"/app = \"$APP_NAME\"/" fly.toml
rm fly.toml.bak

# Deploy the application (force rebuild to ensure latest files are included)
echo "🚀 Deploying application..."
fly deploy --no-cache -a "$APP_NAME"

# Show the status
echo "📊 Deployment status:"
fly status -a "$APP_NAME"

# Show URLs
echo ""
echo "🎉 Deployment complete!"
echo "📊 Public Dashboard: https://$APP_NAME.fly.dev/"
echo "🔐 Admin Interface: https://$APP_NAME.fly.dev/dagster (login: $ADMIN_USERNAME/$ADMIN_PASSWORD)"
echo ""
echo "Useful commands:"
echo "  fly logs -a $APP_NAME                    # View logs"
echo "  fly ssh console -a $APP_NAME            # SSH into the app"
echo "  fly status -a $APP_NAME                 # Check status"
echo "  fly scale count 2 -a $APP_NAME          # Scale to 2 instances"
echo ""
echo "To set up alerting (optional):"
echo "  fly secrets set ANOMSTACK_ALERT_EMAIL_FROM='your-email@domain.com' -a $APP_NAME"
echo "  fly secrets set ANOMSTACK_ALERT_EMAIL_TO='alerts@domain.com' -a $APP_NAME"
echo "  fly secrets set ANOMSTACK_ALERT_EMAIL_PASSWORD='your-app-password' -a $APP_NAME" 