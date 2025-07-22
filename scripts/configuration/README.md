# Configuration Management Scripts

This directory contains scripts for managing Anomstack configuration, including hot-reload capabilities and configuration updates.

## Scripts

### `reload_config.py`
Hot-reload Dagster configuration after making changes to YAML files or environment variables without restarting Docker containers.

**Features:**
- Reloads Dagster workspace and job configurations
- Updates running pipelines with new settings
- Validates configuration before applying changes
- Supports both local and containerized deployments
- Provides detailed reload status and error reporting
- GraphQL API integration for seamless updates

**Use Cases:**
- **Development**: Quickly iterate on metric configurations
- **Production**: Apply configuration changes without downtime
- **Debugging**: Test configuration changes in real-time
- **CI/CD**: Automate configuration deployments

**Usage:**
```bash
cd scripts/configuration/
python reload_config.py
```

**Environment Variables:**
- `DAGSTER_HOST` - Dagster host (default: localhost)
- `DAGSTER_PORT` - Dagster port (default: 3000)

**Prerequisites:**
- Dagster instance must be running and accessible
- GraphQL API must be available
- Valid configuration files in metrics/ directory

## Configuration Hot-Reload Process

The reload process works by:

1. **Validation**: Checks if Dagster instance is accessible
2. **Configuration Loading**: Scans for updated YAML configuration files
3. **Workspace Reload**: Updates Dagster workspace with new configurations
4. **Job Updates**: Refreshes job definitions and schedules
5. **Verification**: Confirms successful reload and reports status

## Supported Configuration Changes

- **Metric Definitions**: Add, modify, or remove metric configurations
- **Data Sources**: Update connection strings and credentials
- **Schedules**: Modify job schedules and timing
- **Alert Settings**: Update notification configurations
- **Processing Parameters**: Change ML model settings and thresholds

## Best Practices

1. **Test Changes Locally**: Validate configuration files before reloading
2. **Backup Configurations**: Keep backups before making changes
3. **Monitor Reload Status**: Check logs for successful reload confirmation
4. **Gradual Updates**: Make incremental changes rather than large overhauls
5. **Environment Consistency**: Ensure development and production configs are synchronized

## Troubleshooting

**Common Issues:**
- **Connection Failed**: Check if Dagster instance is running
- **Invalid Configuration**: Validate YAML syntax and structure
- **Permission Issues**: Ensure proper file access permissions
- **Network Errors**: Verify network connectivity to Dagster instance

**Error Resolution:**
```bash
# Check Dagster status
curl http://localhost:3000/graphql -X POST -H "Content-Type: application/json" -d '{"query": "{ version }"}'

# Validate YAML files
python -c "import yaml; yaml.safe_load(open('path/to/config.yaml'))"

# View detailed logs
python reload_config.py --verbose
```

## Integration with Makefile

This script is integrated with the project Makefile:
- `make reload-config` - Quick config reload
- `make enable-auto-reload` - Enable automatic reloading
- `make enable-config-watcher` - Enable file system watching

## Advanced Usage

**Custom Configuration Paths:**
```bash
METRICS_DIR=/custom/path python reload_config.py
```

**Debug Mode:**
```bash
python reload_config.py --debug --verbose
```

**Specific Configuration Reload:**
```bash
python reload_config.py --config-name specific_metric
```
