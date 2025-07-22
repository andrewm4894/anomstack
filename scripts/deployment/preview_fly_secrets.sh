#!/bin/bash

echo "🔍 Previewing Fly.io secrets configuration..."

# Parse command line arguments for profile support
PROFILE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        -p)
            PROFILE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Function to preview environment variables from .env file (matches deploy_fly.sh)
preview_env_vars_from_file() {
    local env_file="$1"

    if [[ ! -f "$env_file" ]]; then
        echo "❌ No $env_file file found."
        return 1
    fi

    echo "📁 Reading environment variables from $env_file..."

    # Arrays to collect secrets
    declare -a env_vars=()
    declare -a local_only_vars=()

    # Variables that should NOT be sent to Fly (local development only) - UPDATED to match deploy script
    local skip_patterns=(
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
        local should_skip=false
        for pattern in "${skip_patterns[@]}"; do
            if [[ "$line" =~ $pattern ]]; then
                should_skip=true
                local_only_vars+=("$var_name")
                break
            fi
        done

        # Add to appropriate array
        if [[ "$should_skip" == "false" ]]; then
            # Mask sensitive values for preview
            if [[ "$var_name" =~ (PASSWORD|TOKEN|KEY|SECRET) ]]; then
                env_vars+=("$var_name=***MASKED***")
            else
                env_vars+=("$var_name=$var_value")
            fi
        fi

    done < "$env_file"

    # Display summary
    echo ""
    echo "📊 SUMMARY:"
    echo "============"
    if [[ ${#env_vars[@]} -gt 0 ]]; then
        echo "✅ ${#env_vars[@]} variables will be set as Fly secrets (.env takes precedence):"
        printf '  %s\n' "${env_vars[@]}"
    else
        echo "⚠️  No variables found to deploy."
    fi

    echo ""
    if [[ ${#local_only_vars[@]} -gt 0 ]]; then
        echo "🏠 ${#local_only_vars[@]} variables will be SKIPPED (local development only):"
        printf '  %s\n' "${local_only_vars[@]}"
    fi

    echo ""
    echo "🔧 Container-specific paths (always set):"
    echo "  DAGSTER_HOME=/opt/dagster/dagster_home"
    echo "  PYTHONPATH=/opt/dagster/app"

    echo ""
    echo "📋 Fly.io defaults (only set if NOT in your .env):"

    # Check which defaults would be set
    declare -a missing_defaults=()

    if ! grep -q "^DAGSTER_CODE_SERVER_HOST=" "$env_file" 2>/dev/null; then
        missing_defaults+=("DAGSTER_CODE_SERVER_HOST=localhost")
    fi

    if ! grep -q "^ANOMSTACK_DUCKDB_PATH=" "$env_file" 2>/dev/null; then
        missing_defaults+=("ANOMSTACK_DUCKDB_PATH=/data/anomstack.db")
    fi

    if ! grep -q "^ANOMSTACK_MODEL_PATH=" "$env_file" 2>/dev/null; then
        missing_defaults+=("ANOMSTACK_MODEL_PATH=local:///data/models")
    fi

    if ! grep -q "^ANOMSTACK_TABLE_KEY=" "$env_file" 2>/dev/null; then
        missing_defaults+=("ANOMSTACK_TABLE_KEY=metrics")
    fi

    if ! grep -q "^ANOMSTACK_IGNORE_EXAMPLES=" "$env_file" 2>/dev/null; then
        missing_defaults+=("ANOMSTACK_IGNORE_EXAMPLES=no")
    fi

    if [[ ${#missing_defaults[@]} -gt 0 ]]; then
        printf '  %s\n' "${missing_defaults[@]}"
    else
        echo "  ✅ All defaults already defined in your .env - your settings will be used!"
    fi

    echo ""
    echo "🔐 Admin credentials:"
    if grep -q "^ANOMSTACK_ADMIN_PASSWORD=" "$env_file" 2>/dev/null; then
        echo "  ✅ Using admin credentials from your .env"
    else
        echo "  🔐 Random admin password will be generated"
    fi

    echo ""
    echo "💡 To actually deploy with these settings, run:"
    echo "   ./scripts/deployment/deploy_fly.sh [app-name]"
}

# Handle deployment profile if specified (same logic as deploy_fly.sh)
if [[ -n "$PROFILE" ]]; then
    PROFILE_FILE="profiles/${PROFILE}.env"
    if [[ -f "$PROFILE_FILE" ]]; then
        echo "🎯 Using deployment profile: $PROFILE"
        echo "📄 Profile file: $PROFILE_FILE"

        # Create temporary merged .env file
        TEMP_ENV_FILE=$(mktemp)

        # Start with existing .env if it exists
        if [[ -f ".env" ]]; then
            cat ".env" > "$TEMP_ENV_FILE"
            echo "✅ Base configuration loaded from .env"
        else
            touch "$TEMP_ENV_FILE"
        fi

        # Append profile configuration (profile values override .env values)
        echo "" >> "$TEMP_ENV_FILE"  # Add separator
        echo "# Profile: $PROFILE (applied during deployment)" >> "$TEMP_ENV_FILE"
        cat "$PROFILE_FILE" >> "$TEMP_ENV_FILE"
        echo "✅ Profile configuration merged"

        # Use the merged file for preview
        ENV_FILE="$TEMP_ENV_FILE"

        # Run the preview with merged configuration
        preview_env_vars_from_file "$ENV_FILE"

        # Clean up
        rm "$TEMP_ENV_FILE"

    else
        echo "❌ Profile file not found: $PROFILE_FILE"
        echo "Available profiles:"
        ls -1 profiles/*.env 2>/dev/null | sed 's/profiles\///g' | sed 's/\.env//g' | sed 's/^/  - /'
        exit 1
    fi
else
    # Run the standard preview
    preview_env_vars_from_file ".env"
fi
