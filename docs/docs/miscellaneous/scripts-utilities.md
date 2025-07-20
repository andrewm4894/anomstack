---
sidebar_position: 1
---

# Scripts & Utilities

Anomstack includes a collection of utility scripts for common administrative tasks, database management, system maintenance, and development workflows. These scripts are located in the `scripts/` directory.

## 📁 Directory Structure

```
scripts/
├── README.md                    # Overview of all scripts
├── kill_long_running_tasks.py   # Terminate stuck Dagster jobs
├── reload_config.py             # Hot-reload Dagster configuration
├── posthog_example.py           # Test PostHog integration
├── sqlite/                      # SQLite database utilities
│   ├── create_index.py         # Create performance indexes
│   ├── list_tables.py          # List all database tables
│   ├── list_indexes.py         # List all database indexes
│   ├── qry.py                  # Execute custom SQL queries
│   └── qry.sql                 # Example/template SQL query
└── utils/                      # System utilities
    ├── reset_docker.sh         # Docker environment reset tool
    ├── cleanup_dagster_storage.sh # Clean up Dagster storage
    └── README.md               # Utilities documentation
```

## 🔧 Administrative Utilities

### Configuration Hot-Reload
Reload Dagster configuration without restarting containers.

**Script**: `reload_config.py`

```bash
cd scripts/
python reload_config.py
```

**Use Cases:**
- Applied configuration changes to YAML files
- Updated environment variables
- Added new metric batches
- Modified job schedules

**Features:**
- Works with running Docker containers
- Reloads code locations via GraphQL API
- Provides feedback on reload status
- Supports custom Dagster host/port configuration

### Long-Running Task Management
Terminate or mark as failed any Dagster runs that exceed configured timeouts.

**Script**: `kill_long_running_tasks.py`

```bash
cd scripts/
python kill_long_running_tasks.py
```

**Use Cases:**
- Clean up stuck or hanging jobs
- Recover from unresponsive user code servers
- Free up system resources
- Maintenance and cleanup

**Features:**
- Uses same timeout as the timeout sensor (`ANOMSTACK_KILL_RUN_AFTER_MINUTES`)
- Graceful handling of unreachable code servers
- Detailed logging of termination actions
- Automatically marks stuck runs as failed when termination isn't possible

## 🗄️ Database Utilities (SQLite)

For users running Anomstack with SQLite as their database backend.

### Performance Optimization
Create indexes on common metric columns for better query performance.

**Script**: `sqlite/create_index.py`

```bash
cd scripts/sqlite/
python create_index.py
```

**Creates indexes on:**
- `metric_timestamp` - Time-based queries
- `metric_batch` - Batch-based filtering
- `metric_type` - Type-based filtering (metric, score, alert)
- Combined indexes for common query patterns

### Database Inspection
Explore your SQLite database structure and contents.

**List all tables:**
```bash
cd scripts/sqlite/
python list_tables.py
```

**List all indexes:**
```bash
cd scripts/sqlite/
python list_indexes.py
```

### Custom SQL Queries
Execute ad-hoc SQL queries against your SQLite database.

**Script**: `sqlite/qry.py`

```bash
cd scripts/sqlite/
# Edit qry.sql with your custom query first
python qry.py
```

**Example queries:**
```sql
-- Recent anomalies across all metric batches
SELECT 
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value as anomaly_score
FROM metrics 
WHERE metric_type = 'alert' 
    AND metric_value = 1
    AND metric_timestamp >= datetime('now', '-7 days')
ORDER BY metric_timestamp DESC;

-- Top metrics by anomaly count
SELECT 
    metric_batch,
    metric_name,
    COUNT(*) as anomaly_count
FROM metrics 
WHERE metric_type = 'alert' 
    AND metric_value = 1
GROUP BY metric_batch, metric_name
ORDER BY anomaly_count DESC
LIMIT 10;
```

## 🐳 System Utilities

### Docker Environment Reset
Comprehensive Docker reset utility with multiple cleanup levels.

**Script**: `utils/reset_docker.sh`

#### Interactive Mode (Recommended)
```bash
make reset-interactive
```

Provides a guided menu with options:
1. 🔄 **Gentle** - Rebuild containers (safest)
2. 🧹 **Medium** - Remove containers, keep data  
3. ☢️ **Nuclear** - Remove all data and containers
4. 💥 **Full Nuclear** - Nuclear + full Docker cleanup

#### Direct Reset Levels

**Gentle Reset** (Safest - keeps all data):
```bash
make reset-gentle
# or
./scripts/utils/reset_docker.sh gentle
```

**Medium Reset** (Removes containers, preserves data):
```bash
make reset-medium
# or
./scripts/utils/reset_docker.sh medium
```

**Nuclear Reset** (Removes all data):
```bash
make reset-nuclear
# or
./scripts/utils/reset_docker.sh nuclear
```

**Full Nuclear Reset** (Maximum cleanup):
```bash
make reset-full-nuclear
# or
./scripts/utils/reset_docker.sh full-nuclear
```

#### Features
- 📊 Shows current disk usage before cleanup
- ⚠️ Multiple safety confirmations for destructive operations
- 🎨 Colorful output with clear visual feedback
- 🛡️ Graceful fallback handling
- 💾 Always preserves source code and configuration

### Dagster Storage Cleanup
Clean up old Dagster storage files and logs.

**Script**: `utils/cleanup_dagster_storage.sh`

```bash
./scripts/utils/cleanup_dagster_storage.sh
```

**Cleans up:**
- Old compute logs
- Artifact storage files  
- Event log storage
- Run storage artifacts

## 🧪 Development Utilities

### API Integration Testing
Test external service integrations and credentials.

**PostHog Integration Test:**
```bash
cd scripts/
python posthog_example.py
```

Validates that your PostHog API credentials work correctly.

## 📋 Common Usage Patterns

### Daily Maintenance Workflow
```bash
# 1. Clean up any stuck jobs
cd scripts/
python kill_long_running_tasks.py

# 2. Optimize database performance (if using SQLite)
cd sqlite/
python create_index.py

# 3. Check system status
cd ../
python list_tables.py  # Verify data is being written
```

### Configuration Update Workflow
```bash
# 1. Make changes to your YAML configs or .env file
vim metrics/my_metric/config.yaml

# 2. Hot-reload the configuration
cd scripts/
python reload_config.py

# 3. Verify changes took effect in Dagster UI
```

### Database Analysis Workflow
```bash
# 1. Inspect database structure
cd scripts/sqlite/
python list_tables.py
python list_indexes.py

# 2. Run custom analysis queries
vim qry.sql  # Write your analysis query
python qry.py

# 3. Create performance indexes if needed
python create_index.py
```

### System Reset Workflow
```bash
# 1. Interactive guided reset (recommended)
make reset-interactive

# 2. Or direct reset for automation
make reset-gentle      # Safe option
make reset-nuclear     # Clean slate option
```

## 🛠️ Advanced Usage

### Custom Environment Configuration
Most scripts respect environment variables:

```bash
# Custom Dagster endpoint for reload_config.py
export DAGSTER_HOST=dagster.example.com
export DAGSTER_PORT=3000
python reload_config.py

# Custom timeout for kill_long_running_tasks.py
export ANOMSTACK_KILL_RUN_AFTER_MINUTES=120
python kill_long_running_tasks.py

# Custom database path for SQLite scripts
export ANOMSTACK_SQLITE_PATH=/path/to/custom.db
cd sqlite/
python list_tables.py
```

### Automation and Scheduling
Scripts can be integrated into automation workflows:

```bash
#!/bin/bash
# Daily maintenance script

# Clean up stuck jobs
python /path/to/anomstack/scripts/kill_long_running_tasks.py

# Optimize database
python /path/to/anomstack/scripts/sqlite/create_index.py

# Generate daily report
python /path/to/anomstack/scripts/sqlite/qry.py > daily_report.txt
```

### Docker Integration
Some scripts work seamlessly with Docker:

```bash
# Execute scripts inside running containers
docker exec anomstack_code python /opt/dagster/app/scripts/reload_config.py
docker exec anomstack_code python /opt/dagster/app/scripts/kill_long_running_tasks.py
```

## 🔐 Security Considerations

1. **File Permissions**: Ensure scripts have appropriate execute permissions
2. **Database Access**: SQLite scripts require read/write access to database files
3. **Network Access**: Config reload scripts need access to Dagster GraphQL endpoint
4. **Secrets**: Never hardcode credentials in custom scripts

## 💡 Best Practices

1. **Test First**: Always test scripts in development before production use
2. **Backup Data**: Create backups before running destructive operations
3. **Monitor Logs**: Check script output and logs for errors
4. **Document Changes**: Keep track of when and why you run scripts
5. **Version Control**: Track any modifications to scripts in version control

## 🆘 Troubleshooting

### Common Issues

**Script can't find database:**
```bash
# Set the correct database path
export ANOMSTACK_SQLITE_PATH=/path/to/your/database.db
```

**Config reload fails:**
```bash
# Check if Dagster is running and accessible
curl http://localhost:3000/server_info
```

**Permission denied errors:**
```bash
# Make scripts executable
chmod +x scripts/utils/reset_docker.sh
```

**SQLite locked errors:**
```bash
# Stop Anomstack before running database scripts
make docker-stop
cd scripts/sqlite/
python your_script.py
make docker
```

### Getting Help

- Check individual script help: `python script_name.py --help`
- Review README files in each directory
- Check Dagster UI for job status and logs
- Use interactive modes when available (`make reset-interactive`) 