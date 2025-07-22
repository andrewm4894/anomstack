# Deployment Scripts

This directory contains scripts for deploying Anomstack to various cloud platforms.

## Fly.io Deployment

### `deploy_fly.sh`
Automated deployment script for Fly.io platform.

**Features:**
- Validates Fly CLI installation and authentication
- Checks for required configuration files
- Deploys Anomstack to Fly.io with proper configuration
- Handles environment variable management
- Provides detailed deployment status and logging

**Prerequisites:**
- Fly CLI installed and configured (`fly auth login`)
- Valid `fly.toml` configuration file
- Proper Dockerfile and Dagster configuration for Fly.io

**Usage:**
```bash
cd scripts/deployment/
./deploy_fly.sh
```

### `validate_fly_config.sh`
Configuration validation script for Fly.io deployments.

**Features:**
- Validates all required files are present
- Checks Fly.io configuration syntax
- Verifies Docker and Dagster configuration files
- Tests environment variable setup
- Provides detailed validation report

**Usage:**
```bash
cd scripts/deployment/
./validate_fly_config.sh
```

## Common Use Cases

- **Initial Deployment**: Set up Anomstack on Fly.io from scratch
- **Configuration Updates**: Deploy configuration changes
- **Pre-deployment Validation**: Ensure all files are properly configured
- **CI/CD Integration**: Automate deployments in pipelines

## Best Practices

1. **Always validate configuration** before deploying with `validate_fly_config.sh`
2. **Test in development** environment first
3. **Review logs** during and after deployment
4. **Keep credentials secure** - use Fly.io secrets management
5. **Monitor resource usage** after deployment

## Required Files for Fly.io

- `fly.toml` - Fly.io application configuration
- `docker/Dockerfile.fly` - Fly.io-specific Dockerfile
- `dagster_fly.yaml` - Dagster configuration for Fly.io
- `dagster_home/workspace.yaml` - Dagster workspace configuration (environment-aware)
- Environment variables properly configured

## Troubleshooting

**Common Issues:**
- Missing Fly CLI authentication: Run `fly auth login`
- Configuration file errors: Use `validate_fly_config.sh` to identify issues
- Resource allocation: Check Fly.io app settings for memory/CPU limits
- Environment variables: Ensure all required secrets are set in Fly.io

**Getting Help:**
- Check Fly.io logs: `fly logs`
- Validate configuration: `./validate_fly_config.sh`
- Review Fly.io documentation: https://fly.io/docs/
