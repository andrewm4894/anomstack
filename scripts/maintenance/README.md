# Maintenance Scripts

This directory contains scripts for system maintenance, cleanup, and operational tasks to keep your Anomstack deployment running smoothly.

## Scripts

### `kill_long_running_tasks.py`
Dagster utility for terminating or marking as failed any runs that exceed the configured timeout.

**Features:**
- Uses the same timeout configuration as the timeout sensor
- Gracefully handles unreachable user code servers
- Provides detailed logging of termination actions
- Automatically marks stuck runs as failed when termination isn't possible
- Safe cleanup of orphaned or zombie processes
- Prevents resource exhaustion from stuck jobs

**Use Cases:**
- **Stuck Jobs**: Terminate jobs that exceed normal runtime
- **Resource Management**: Free up system resources from hung processes
- **Automated Cleanup**: Schedule regular cleanup of long-running tasks
- **Development**: Clean up test runs that got stuck during development
- **Production Maintenance**: Ensure system reliability by cleaning up failed jobs

**Usage:**
```bash
cd scripts/maintenance/
python kill_long_running_tasks.py
```

**Configuration:**
- Timeout settings are read from the same configuration as the timeout sensor
- Default timeout can be overridden with environment variables
- Supports different timeout values for different job types

**Safety Features:**
- **Graceful Termination**: Attempts graceful shutdown before force-killing
- **Logging**: Detailed logs of all termination actions
- **Validation**: Checks job status before taking action
- **Error Handling**: Handles unreachable user code servers gracefully

### `cleanup_disk_space.py`
Standalone script for managing disk space by cleaning up old artifacts, logs, and metrics.

**Features:**
- **Artifact Cleanup**: Removes old Dagster run artifacts
- **Log Cleanup**: Removes old log files from multiple directories
- **Database Cleanup**: Removes old metrics and vacuums database
- **Disk Usage Reporting**: Shows before/after disk usage statistics
- **Dry Run Mode**: Preview cleanup without making changes
- **Aggressive Mode**: More thorough cleanup for emergency situations

**Use Cases:**
- **Emergency Cleanup**: Free disk space when volume is full
- **Scheduled Maintenance**: Regular cleanup to prevent disk issues
- **Deployment Optimization**: Optimize Fly.io volume usage
- **Development**: Clean up after testing

**Usage:**
```bash
# Preview what would be cleaned up
python cleanup_disk_space.py --dry-run

# Normal cleanup (6h artifacts, 24h logs)
python cleanup_disk_space.py

# Aggressive cleanup (1h artifacts, all logs)
python cleanup_disk_space.py --aggressive

# Emergency cleanup with preview
python cleanup_disk_space.py --dry-run --aggressive
```

**Cleanup Targets:**
- **Artifacts**: Dagster run artifacts older than 6 hours (1 hour in aggressive mode)
- **Logs**: Log files older than 24 hours (all logs in aggressive mode)
- **Database**: Metrics older than 90 days + VACUUM operation
- **Locations**: `/data/artifacts`, `/tmp/dagster`, `/data/dagster_storage`

**Safety Features:**
- **Dry Run Mode**: Safe preview of cleanup actions
- **Detailed Reporting**: Shows exactly what will be/was removed
- **Error Handling**: Continues cleanup even if individual files fail
- **Size Calculation**: Reports space freed by cleanup operations

## Common Maintenance Tasks

### Regular Cleanup Operations
- **Job Cleanup**: Remove completed and failed job runs older than retention period
- **Log Rotation**: Archive or delete old log files
- **Storage Cleanup**: Remove temporary files and optimize database storage
- **Performance Monitoring**: Check system resource usage and performance

### Troubleshooting Operations
- **Stuck Process Investigation**: Identify and resolve hanging processes
- **Resource Usage Analysis**: Monitor CPU, memory, and disk usage
- **Error Analysis**: Review error logs and identify recurring issues
- **Performance Bottlenecks**: Identify and resolve performance issues

## Best Practices

1. **Schedule Regular Maintenance**: Run cleanup scripts on a regular schedule
2. **Monitor Before Acting**: Always check system status before running maintenance
3. **Backup Critical Data**: Ensure backups are current before cleanup operations
4. **Test in Development**: Validate maintenance scripts in development environment
5. **Document Actions**: Keep logs of maintenance activities
6. **Gradual Cleanup**: Avoid aggressive cleanup that might impact running jobs

## Integration with Other Systems

**Dagster Integration:**
- Reads timeout configuration from Dagster settings
- Uses Dagster API for job management
- Respects Dagster's job lifecycle and status

**Docker Integration:**
- Works with containerized Dagster instances
- Handles container-specific process management
- Compatible with Docker networking

**Monitoring Integration:**
- Can be integrated with monitoring systems
- Provides metrics on cleanup operations
- Supports alerting on maintenance issues

## Troubleshooting

**Common Issues:**
- **Permission Errors**: Ensure script has proper permissions to terminate processes
- **Connection Issues**: Verify Dagster instance is accessible
- **Configuration Errors**: Check timeout settings and environment variables

**Error Resolution:**
```bash
# Check Dagster instance status
dagster instance info

# View current running jobs
dagster job list

# Check system resources
top -p $(pgrep -f dagster)

# View detailed script output
python kill_long_running_tasks.py --verbose
```

**Environment Variables:**
- `DAGSTER_HOME` - Path to Dagster home directory
- `ANOMSTACK_DAGSTER_*` - Various Dagster configuration settings
- Timeout settings from main configuration

## Automation and Scheduling

**Cron Integration:**
```bash
# Run cleanup every hour
0 * * * * /path/to/scripts/maintenance/kill_long_running_tasks.py

# Run cleanup every 6 hours with logging
0 */6 * * * /path/to/scripts/maintenance/kill_long_running_tasks.py >> /var/log/anomstack-cleanup.log 2>&1
```

**Docker Compose Integration:**
Add as a scheduled service in docker-compose.yaml for automatic cleanup.

**Dagster Schedule Integration:**
Create Dagster schedules to run maintenance tasks as part of normal operations.

## Monitoring and Alerting

**Success Metrics:**
- Number of jobs terminated
- System resource usage before/after cleanup
- Cleanup execution time

**Alert Conditions:**
- Excessive number of stuck jobs
- Cleanup script failures
- Resource usage issues

**Logging:**
All maintenance activities are logged with timestamps and details for audit purposes.
