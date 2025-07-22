---
sidebar_position: 2
---

# Hot Configuration Updates

This guide explains how to update Anomstack configurations dynamically without restarting Docker containers.

## 🔥 What's New

With the updated Docker setup, you can now:

- **Update YAML configs** in `/metrics` and see changes immediately
- **Modify environment variables** in `.env` (requires container restart)
- **Add new metric batches** without rebuilding images
- **Change SQL queries or Python functions** on the fly
- **Reload Dagster** with a single command

## 🚀 Quick Start

### Option 1: Manual Reload (On-Demand)

```bash
# 1. Make changes to YAML files in /metrics/
vim metrics/my_batch/config.yaml

# 2. Reload manually
make reload-config
```

### Option 2: Automatic Scheduled Reload

```bash
# Enable automatic reload every 5 minutes
make enable-auto-reload

# Restart containers to activate
make docker-restart
```

### Option 3: Smart File Watcher (Recommended)

```bash
# Enable smart file watching (reloads only when files change)
make enable-config-watcher

# Restart containers to activate
make docker-restart
```

That's it! Your changes will now be automatically detected and applied.

## 📋 What Works with Hot Reload

### ✅ YAML Configuration Changes
- Metric batch configurations (`metrics/*/*.yaml`)
- Default settings (`metrics/defaults/defaults.yaml`)
- Schedule configurations
- Alert thresholds and settings
- Database connection parameters (except connection strings)

### ✅ SQL Query Updates
- Ingest SQL queries (`ingest_sql` or `ingest_sql_file`)
- Custom SQL templates
- Query logic changes

### ✅ Python Function Updates
- Custom ingest functions (`ingest_fn`)
- Preprocessing functions
- Python-based metric calculations

### ✅ New Metric Batches
- Adding entirely new metric batch folders
- New YAML + SQL/Python combinations

### ⚠️ Requires Manual Container Restart
- Environment variable changes in `.env`
- Database connection string changes
- Infrastructure-level changes

For `.env` file changes, use this workflow:
```bash
# 1. Edit environment variables
vim .env

# 2. Restart containers to pick up new environment variables
make docker-restart  # or docker compose restart

# 3. Reload configuration (optional - to be safe)
make reload-config
```

## 🤖 Automated Reloading Options

### Scheduled Job (Option 2)
- **How it works**: Runs a Dagster job every N minutes to reload configurations
- **Best for**: Development environments where you want periodic updates
- **Configuration**:
  ```bash
  ANOMSTACK_AUTO_CONFIG_RELOAD=true           # Enable the feature
  ANOMSTACK_CONFIG_RELOAD_CRON="*/5 * * * *"   # Every 5 minutes
  ANOMSTACK_CONFIG_RELOAD_STATUS=RUNNING      # Start the schedule
  ```
- **Pros**: Simple, predictable timing
- **Cons**: May reload unnecessarily, slight resource usage

### Smart File Watcher (Option 3) - **Recommended**
- **How it works**: Monitors YAML files for changes, reloads only when needed
- **Best for**: Production and development - most efficient approach
- **Scope**: **YAML files only** - .env changes still require manual restart
- **Configuration**:
  ```bash
  ANOMSTACK_CONFIG_WATCHER=true              # Enable the sensor
  ANOMSTACK_CONFIG_WATCHER_INTERVAL=30       # Check every 30 seconds
  ```
- **Pros**: Only reloads when necessary, most responsive, resource efficient
- **Cons**: Doesn't handle .env changes (by design for safety)

### How File Watching Works
1. **Hash Calculation**: Creates MD5 hash of all YAML files (content + modification time)
2. **Change Detection**: Compares current hash with last known state
3. **Smart Reloading**: Only triggers reload when YAML files actually change
4. **State Persistence**: Remembers last known state across Dagster restarts

**Note**: File watcher intentionally excludes `.env` files to avoid complex container restart scenarios that could cause side effects.

## 🔧 How It Works

The hot reload system works by:

1. **Volume Mounting**: The `/metrics` directory is now mounted as a volume in Docker containers
2. **Dagster Code Location Reload**: Uses Dagster's built-in GraphQL API to reload code locations
3. **Configuration Re-parsing**: The `get_specs()` function re-reads YAML files from the mounted directory

### Before (Required Container Rebuild)
```
Host /metrics → Docker Image (frozen at build time) → Container
```

### After (Hot Reload Enabled)
```
Host /metrics → Docker Volume Mount → Container (live updates)
```

## 📝 Updated Docker Configuration

### Volume Mounts Added
The following services now mount the metrics directory:

```yaml
# docker-compose.yaml
anomstack_code:
  volumes:
    - ./metrics:/opt/dagster/app/metrics  # 🔥 NEW

anomstack_webserver:
  volumes:
    - ./metrics:/opt/dagster/app/metrics  # 🔥 NEW

anomstack_daemon:
  volumes:
    - ./metrics:/opt/dagster/app/metrics  # 🔥 NEW

# dagster_docker.yaml (for job containers)
run_launcher:
  config:
    container_kwargs:
      volumes:
        - /path/to/metrics:/opt/dagster/app/metrics  # 🔥 NEW
```

## 🔄 Configuration Reload Script

The `scripts/reload_config.py` script:

- ✅ Validates configuration files are accessible
- ✅ Checks Dagster health before attempting reload
- ✅ Uses GraphQL API to reload code locations
- ✅ Provides clear success/error messages
- ✅ Shows loaded repositories after reload

### Script Usage
```bash
# From anomstack root directory
python3 scripts/reload_config.py

# Via Makefile
make reload-config
```

## 🛠️ Troubleshooting

### Configuration Reload Failed
```bash
# Check container status
docker compose ps

# Check Dagster logs
docker compose logs anomstack_code

# Restart specific service if needed
docker compose restart anomstack_code

# Full restart if required
docker compose restart
```

### Volume Mount Issues
If configurations aren't updating:

1. Verify volume mounts:
   ```bash
   docker compose exec anomstack_code ls -la /opt/dagster/app/metrics
   ```

2. Check file permissions:
   ```bash
   # Ensure metrics directory is readable
   chmod -R 755 metrics/
   ```

### Environment Variable Updates
For `.env` file changes, use the manual workflow:

```bash
# 1. Edit your environment variables
vim .env

# 2. Restart containers (required for env var changes)
make docker-restart

# 3. Optional: Reload configs to be safe
make reload-config
```

**Why manual?** Container restarts require careful orchestration. Automated restart could cause side effects, so we keep this as an explicit, predictable user action.

## 🎯 Best Practices

### 1. Test Changes Gradually
- Make small, incremental changes
- Test each change with `make reload-config`
- Monitor Dagster UI for successful reloads

### 2. Validate Configurations
- Use the reload script to catch syntax errors early
- Check Dagster logs if reload fails
- Keep backup copies of working configurations

### 3. Environment vs YAML
- Use YAML for business logic (thresholds, schedules, SQL)
- Use environment variables for secrets and deployment-specific settings
- Use environment variable overrides for testing different values

### 4. Version Control
- Commit configuration changes to git
- Use branching for experimental configurations
- Document breaking changes in commit messages

## 🔍 Monitoring Changes

### Dagster UI
- Visit http://localhost:3000
- Check "Workspace" tab for reload status
- Monitor "Runs" tab for job execution

### Dashboard
- Visit http://localhost:5001
- Verify metric batches appear correctly
- Check that data flows as expected

### Logs
```bash
# Watch all services
docker compose logs -f

# Focus on specific service
docker compose logs -f anomstack_code
```

## 🚨 Migration Notes

If you're updating from a previous version:

1. **Pull latest changes** including Docker configuration updates
2. **Restart containers** to apply volume mounts:
   ```bash
   docker compose down
   docker compose up -d
   ```
3. **Test hot reload** with a small configuration change
4. **Update your workflow** to use `make reload-config` instead of container restarts

## 💡 Advanced Usage

### Custom Dagster Host/Port
```bash
# If running Dagster on different host/port
DAGSTER_HOST=my-host DAGSTER_PORT=3001 python3 scripts/reload_config.py
```

### Multiple Code Locations
```python
# Modify scripts/reload_config.py to reload specific locations
reload_code_location("my_custom_location")
```

### Automated Reloading
```bash
# Use with file watching tools for automatic reload
# (Not recommended for production)
fswatch -o metrics/ | xargs -n1 -I{} make reload-config
```

## 🎉 Benefits

### Manual Reload
- **🚀 Faster Development**: No more waiting for container rebuilds
- **🔄 Quick Iterations**: Test configuration changes in seconds
- **💡 Better UX**: Immediate feedback on configuration changes

### Automated Reload (YAML Files Only)
- **🤖 Zero Intervention**: Set it and forget it - YAML configs update automatically
- **⚡ Real-time Updates**: YAML changes detected and applied within seconds
- **🎯 Smart Detection**: Only reloads when YAML files actually change
- **📊 Dagster Integration**: Full visibility in Dagster UI (jobs, sensors, logs)
- **🛡️ Production Ready**: Robust error handling and logging
- **🔒 Safe by Design**: Avoids complex container restart automation

### Overall
- **🛡️ Safer Operations**: Avoid full container restarts in production
- **📈 Improved Productivity**: Spend more time on analysis, less on deployment
- **🔍 Full Observability**: All reload attempts logged and trackable in Dagster

---

*This feature requires Anomstack v1.x+ with updated Docker configurations.*
