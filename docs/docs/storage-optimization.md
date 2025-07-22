---
sidebar_position: 3
title: Storage Optimization
description: Prevent Dagster storage buildup and manage disk space effectively
---

# Dagster Storage Optimization

## The Problem: Excessive Storage Buildup

During development, Dagster can accumulate massive amounts of storage data if not properly configured. This can lead to:

- **212,000+ run directories** in `tmp/`
- **63GB+ of accumulated storage**
- System performance degradation
- Disk space exhaustion

## Root Causes

1. **No retention policies** configured by default
2. **High concurrent runs** (25+ simultaneous) creating many artifacts
3. **Indefinite storage** of compute logs and run metadata
4. **No automatic cleanup** of old runs
5. **Large temp directories** without size limits

## Solutions Implemented

### 1. Configuration Improvements

#### Updated `dagster.yaml`
```yaml
retention:
  schedule:
    purge_after_days: 3  # Reduced from 7
  sensor:
    purge_after_days:
      skipped: 1   # Keep only 1 day of skipped runs  
      failure: 3   # Keep 3 days of failures for debugging
      success: 1   # Keep only 1 day of successful runs
```

#### Updated `dagster_docker.yaml`
```yaml
run_coordinator:
  config:
    max_concurrent_runs: 10  # Reduced from 25

# Added retention policies
retention:
  schedule:
    purge_after_days: 3
  sensor:
    purge_after_days:
      skipped: 1
      failure: 3  
      success: 1

# Added run monitoring
run_monitoring:
  enabled: true
  start_timeout_seconds: 300
  cancel_timeout_seconds: 180
  max_runtime_seconds: 3600
  poll_interval_seconds: 60

# Disabled telemetry to reduce disk writes
telemetry:
  enabled: false
```

### 2. Automated Cleanup Tools

#### Cleanup Script: `scripts/utils/cleanup_dagster_storage.sh`

**Interactive Menu:**
```bash
./scripts/utils/cleanup_dagster_storage.sh
# or
make dagster-cleanup-menu
```

**Direct Commands:**
```bash
# Check current status
make dagster-cleanup-status

# Safe cleanup (recommended)
make dagster-cleanup-minimal

# Remove old runs (30+ days)
make dagster-cleanup-standard

# Aggressive cleanup (7+ days)
make dagster-cleanup-aggressive
```

#### Cleanup Levels:

1. **Minimal** (🔧): Remove old logs only - safe for production
2. **Standard** (🧹): Remove runs older than 30 days
3. **Aggressive** (🔥): Remove runs older than 7 days  
4. **Nuclear** (☢️): Remove all but last 24 hours
5. **CLI-based** (🛠️): Use Dagster's built-in cleanup commands

### 3. Environment Variable Updates

Updated `.example.env` with lightweight defaults:
```bash
# Lightweight storage paths
ANOMSTACK_DAGSTER_LOCAL_ARTIFACT_STORAGE_DIR=tmp_light/artifacts
ANOMSTACK_DAGSTER_LOCAL_COMPUTE_LOG_MANAGER_DIRECTORY=tmp_light/compute_logs
ANOMSTACK_DAGSTER_SQLITE_STORAGE_BASE_DIR=tmp_light/storage

# Reduced concurrency
ANOMSTACK_DAGSTER_OVERALL_CONCURRENCY_LIMIT=5  # Reduced from 10
ANOMSTACK_DAGSTER_DEQUEUE_NUM_WORKERS=2        # Reduced from 4
```

## Best Practices

### For Developers

1. **Regular Monitoring:**
   ```bash
   make dagster-cleanup-status  # Check storage weekly
   ```

2. **Routine Cleanup:**
   ```bash
   make dagster-cleanup-minimal  # Weekly log cleanup
   make dagster-cleanup-standard # Monthly run cleanup
   ```

3. **Emergency Cleanup:**
   ```bash
   make dagster-cleanup-aggressive  # When disk space is low
   ```

### For Production

1. **Configure retention policies** in `dagster_docker.yaml`
2. **Limit concurrent runs** to reasonable numbers (5-15)
3. **Enable run monitoring** to detect stuck runs
4. **Set up automated cleanup** using cron jobs:
   ```bash
   # Weekly cleanup cron job
   0 2 * * 0 /path/to/cleanup_dagster_storage.sh minimal

   # Monthly aggressive cleanup
   0 3 1 * * /path/to/cleanup_dagster_storage.sh standard
   ```

### For CI/CD

1. **Use ephemeral storage** when possible
2. **Clean up after tests:**
   ```bash
   make dagster-cleanup-aggressive
   ```
3. **Monitor disk usage** in build scripts

## Storage Size Guidelines

| Storage Level | Recommended Action |
|---------------|-------------------|
| < 1GB | ✅ Healthy - continue monitoring |
| 1-5GB | ⚠️ Consider weekly cleanup |
| 5-20GB | 🔄 Run standard cleanup monthly |
| 20-50GB | 🔥 Run aggressive cleanup |
| > 50GB | ☢️ Emergency cleanup required |

## Troubleshooting

### Issue: "212,000+ run directories"
**Solution:** Run nuclear cleanup, then configure retention policies

### Issue: "Disk space full"
**Solution:**
1. Run `make dagster-cleanup-aggressive`
2. If still full, run `make reset-nuclear`
3. Configure retention policies before restarting

### Issue: "Slow Dagster performance"
**Solution:**
1. Check storage with `make dagster-cleanup-status`
2. Run appropriate cleanup level
3. Reduce `max_concurrent_runs`

### Issue: "Old runs not being cleaned up"
**Solution:**
1. Verify retention policies in `dagster_docker.yaml`
2. Ensure Dagster daemon is running
3. Check database connectivity for PostgreSQL storage

## Prevention Checklist

- [ ] Retention policies configured in `dagster_docker.yaml`
- [ ] Run monitoring enabled
- [ ] Concurrent runs limited (≤ 15)
- [ ] Regular cleanup scheduled (weekly/monthly)
- [ ] Storage monitoring in place
- [ ] Telemetry disabled in production
- [ ] Environment variables optimized

## Additional Resources

- **Interactive Cleanup**: `make dagster-cleanup-menu`
- **Makefile Documentation**: Available in the project root `Makefile.md#dagster-storage-cleanup`
- **Reset Scripts**: Available in `scripts/utils/` directory  
- **Dagster Retention Docs**: [Official Documentation](https://docs.dagster.io/deployment/run-monitoring)

---

**💡 Key Takeaway**: Proactive storage management prevents the 63GB+ buildup problem. Regular monitoring and cleanup are essential for healthy Dagster deployments.
