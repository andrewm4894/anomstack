# Scripts Directory

This directory contains utility scripts and tools for managing and maintaining your Anomstack deployment.

## Overview

The scripts in this directory provide helpful utilities for common administrative tasks, database setup, data migration, and development workflows.

## Structure

### `sqlite/`
Contains SQLite-specific utility scripts for users running Anomstack with SQLite as their database backend.

### `posthog_example.py`
Runs the PostHog metrics ingest function to ensure your PostHog credentials work.

## Common Use Cases

These scripts are typically used for:

- **Database Setup**: Initialize databases and create required tables
- **Data Migration**: Move data between different storage backends
- **Maintenance**: Clean up old data, optimize performance
- **Development**: Setup development environments and test data
- **Deployment**: Automate deployment tasks and configuration

## Usage

Most scripts can be run directly from the command line:

```bash
# Navigate to the scripts directory
cd scripts/

# Run a specific script
python script_name.py
```

## Database-Specific Scripts

Different database backends may have specific requirements and utilities:

- **SQLite**: Scripts for local development and small deployments
- **DuckDB**: Utilities for analytical workloads
- **Cloud Databases**: Migration and setup scripts for cloud platforms

## Contributing Scripts

When adding new utility scripts:

1. Place them in the appropriate subdirectory based on their purpose
2. Include clear documentation and usage examples
3. Add error handling and logging
4. Test scripts thoroughly before committing
5. Update this README with information about new scripts

## Best Practices

- Always test scripts in a development environment first
- Include proper error handling and rollback mechanisms
- Document any prerequisites or dependencies
- Use appropriate logging levels for different operations
- Follow the project's coding standards and conventions
