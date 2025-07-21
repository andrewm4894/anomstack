# Scripts Directory

This directory contains utility scripts and tools organized by category for managing and maintaining your Anomstack deployment.

## Directory Structure

The scripts are organized into descriptive subfolders based on their purpose:

### 📁 [`deployment/`](deployment/)
Scripts for deploying Anomstack to cloud platforms:
- **`deploy_fly.sh`** - Automated Fly.io deployment with **NEW! .env integration** 🎉
- **`preview_fly_secrets.sh`** - **NEW!** Preview what environment variables will be deployed as Fly secrets
- **`validate_fly_config.sh`** - Pre-deployment configuration validation for Fly.io

### 📁 [`configuration/`](configuration/)
Scripts for managing Anomstack configuration:
- **`reload_config.py`** - Hot-reload Dagster configuration without container restarts

### 📁 [`maintenance/`](maintenance/)
Scripts for system maintenance and cleanup:
- **`kill_long_running_tasks.py`** - Terminate stuck Dagster runs and cleanup resources

### 📁 [`examples/`](examples/)
Example scripts for testing integrations and validating setup:
- **`posthog_example.py`** - Test PostHog integration and validate credentials

### 📁 [`sqlite/`](sqlite/)
SQLite-specific database utilities (existing):
- **`create_index.py`** - Create performance indexes on common columns
- **`list_tables.py`** - List all database tables with details
- **`list_indexes.py`** - List all database indexes
- **`qry.py`** - Execute ad-hoc SQL queries from qry.sql file

### 📁 [`utils/`](utils/)
General system utilities (existing):
- **`reset_docker.sh`** - Comprehensive Docker environment reset with multiple cleanup levels
- **`cleanup_dagster_storage.sh`** - Clean up old Dagster runs and storage

## Quick Start Guide

### Common Administrative Tasks

**Deploy to Fly.io:**
```bash
# New! Automatic .env integration
cd scripts/deployment/
cp ../../.example.env ../../.env      # Edit with your secrets
./preview_fly_secrets.sh              # Preview what will be deployed
./validate_fly_config.sh              # Validate configuration first
./deploy_fly.sh                       # Deploy with your environment variables
```

**Configuration Management:**
```bash
cd scripts/configuration/
python reload_config.py  # Hot-reload configurations
```

**System Maintenance:**
```bash
cd scripts/maintenance/
python kill_long_running_tasks.py  # Clean up stuck jobs

cd scripts/utils/
./cleanup_dagster_storage.sh       # Clean up old Dagster data
```

**Integration Testing:**
```bash
cd scripts/examples/
python posthog_example.py  # Test PostHog integration
```

**Database Operations:**
```bash
cd scripts/sqlite/
python create_index.py    # Optimize database performance
python list_tables.py     # Inspect database structure
```

## Script Categories Explained

### 🚀 **Deployment Scripts**
Handle deployment to cloud platforms with proper validation, configuration management, and error handling. These scripts ensure reliable deployment processes and provide comprehensive validation before deployment.

### ⚙️ **Configuration Scripts** 
Enable hot-reloading of configurations without service restarts. Essential for development workflows and production configuration updates without downtime.

### 🔧 **Maintenance Scripts**
Keep your Anomstack deployment running smoothly by cleaning up stuck processes, managing resources, and performing regular maintenance tasks.

### 🧪 **Example Scripts**
Validate integrations, test connectivity, and provide working examples of how to interact with external services. Useful for troubleshooting and learning.

### 🗄️ **Database Scripts**
Database-specific utilities for performance optimization, inspection, and maintenance. Currently focused on SQLite but can be extended for other databases.

### 🛠️ **General Utils**
System-level utilities for environment management, cleanup operations, and general administrative tasks.

## Usage Patterns

### Development Workflow
1. **Setup**: Use example scripts to validate integrations
2. **Configure**: Use configuration scripts for hot-reloading during development
3. **Maintain**: Use maintenance scripts to clean up development artifacts
4. **Deploy**: Use deployment scripts for testing deployments

### Production Operations
1. **Deploy**: Use deployment scripts with proper validation
2. **Monitor**: Use maintenance scripts for regular cleanup
3. **Update**: Use configuration scripts for zero-downtime updates
4. **Troubleshoot**: Use example scripts to validate external dependencies

### Database Administration
1. **Optimize**: Use database scripts to create indexes and optimize performance
2. **Inspect**: Use database scripts to understand schema and structure
3. **Query**: Use database scripts for ad-hoc analysis and troubleshooting
4. **Maintain**: Use database scripts for cleanup and maintenance

## Best Practices

### Security
- Always validate scripts in development before production use
- Use environment variables for sensitive configuration
- Review scripts for security implications before execution
- Keep credentials out of script files

### Reliability
- Test scripts thoroughly in development environments
- Include proper error handling and rollback mechanisms
- Use appropriate logging levels for different operations
- Document prerequisites and dependencies clearly

### Maintenance
- Keep scripts updated with system changes
- Include proper documentation and usage examples
- Follow consistent naming and organization patterns
- Regular review and cleanup of obsolete scripts

## Integration with Makefile

Many scripts are integrated with the project Makefile for convenience:

- `make reload-config` → `scripts/configuration/reload_config.py`
- `make reset-interactive` → `scripts/utils/reset_docker.sh`
- `make dagster-cleanup-standard` → `scripts/utils/cleanup_dagster_storage.sh`

See the main project Makefile for complete integration details.

## Contributing New Scripts

When adding new utility scripts:

1. **Choose the Right Category**: Place scripts in the appropriate subdirectory
2. **Follow Naming Conventions**: Use descriptive, consistent names
3. **Include Documentation**: Add comprehensive README updates and inline documentation
4. **Add Error Handling**: Include proper error handling and user feedback
5. **Test Thoroughly**: Validate scripts in development environments
6. **Update Documentation**: Keep README files current with new functionality

### Creating New Categories

If you need a new category:
1. Create the subdirectory with a descriptive name
2. Add a comprehensive README.md file
3. Update this main README with the new category
4. Consider Makefile integration for common operations

## Support and Troubleshooting

Each subdirectory contains detailed README files with:
- Specific usage instructions
- Troubleshooting guidance
- Common use cases and examples
- Integration details and requirements

For general issues:
- Check script permissions and execution environment
- Verify all prerequisites and dependencies are met
- Review logs and error output for specific guidance
- Test in development environment before production use
