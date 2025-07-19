# Scripts Directory

This directory contains utility scripts and tools for managing and maintaining your Anomstack deployment.

## Overview

The scripts in this directory provide helpful utilities for common administrative tasks, database setup, data migration, and development workflows.

## Structure

### `kill_long_running_tasks.py`
Dagster utility for terminating or marking as failed any runs that exceed the configured timeout. 

**Features:**
- Uses the same timeout configuration as the timeout sensor
- Gracefully handles unreachable user code servers
- Provides detailed logging of termination actions
- Automatically marks stuck runs as failed when termination isn't possible

**Usage:**
```bash
cd scripts/
python kill_long_running_tasks.py
```

### `posthog_example.py`
Runs the PostHog metrics ingest function to ensure your PostHog credentials work.

### `sqlite/`
Contains SQLite-specific utility scripts for users running Anomstack with SQLite as their database backend:

#### `create_index.py`
Automatically creates performance indexes on common metric columns (`metric_timestamp`, `metric_batch`, `metric_type`) for all tables in the SQLite database.

**Usage:**
```bash
cd scripts/sqlite/
python create_index.py
```

#### `list_tables.py`
Lists all tables in the SQLite database with their names and details.

**Usage:**
```bash
cd scripts/sqlite/
python list_tables.py
```

#### `list_indexes.py`
Lists all indexes in the SQLite database with their names and associated tables.

**Usage:**
```bash
cd scripts/sqlite/
python list_indexes.py
```

#### `qry.py`
Executes the SQL query from `qry.sql` file and returns results as a DataFrame. Useful for running ad-hoc SQL queries against your SQLite database.

**Usage:**
```bash
cd scripts/sqlite/
# Edit qry.sql with your query first
python qry.py
```

### `utils/`
Contains general utility scripts for system management and maintenance.

### `utils/reset_docker.sh`
Comprehensive Docker reset utility with multiple cleanup levels:
- **Gentle**: Rebuild containers with fresh images (safest)
- **Medium**: Remove containers and networks, preserve data volumes
- **Nuclear**: Remove all data including volumes and local files
- **Full Nuclear**: Nuclear reset + complete Docker system cleanup

Can be run interactively or with specific reset levels via Makefile targets.

## Common Use Cases

These scripts are typically used for:

- **Database Setup**: Initialize databases and create required tables
- **Database Performance**: Create indexes to improve query performance (`create_index.py`)
- **Database Inspection**: View table and index structures (`list_tables.py`, `list_indexes.py`)
- **Data Migration**: Move data between different storage backends
- **Data Analysis**: Run ad-hoc SQL queries for troubleshooting (`qry.py`)
- **Maintenance**: Clean up old data, optimize performance
- **Task Management**: Terminate stuck or long-running Dagster jobs (`kill_long_running_tasks.py`)
- **Development**: Setup development environments and test data
- **Deployment**: Automate deployment tasks and configuration
- **System Reset**: Clean up Docker environments with various levels of data preservation (`reset_docker.sh`)
- **Credential Validation**: Test external service integrations (`posthog_example.py`)

## Usage

Most scripts can be run directly from the command line:

```bash
# Navigate to the scripts directory
cd scripts/

# Run a specific script
python script_name.py
```

### Quick Examples

**Database performance optimization:**
```bash
cd scripts/sqlite/
python create_index.py  # Create performance indexes
```

**Database inspection:**
```bash
cd scripts/sqlite/
python list_tables.py   # See all tables
python list_indexes.py  # See all indexes
```

**Clean up stuck Dagster jobs:**
```bash
cd scripts/
python kill_long_running_tasks.py
```

**Complete Docker environment reset:**
```bash
make reset-interactive  # Interactive mode
# or
make reset-nuclear      # Nuclear reset
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
