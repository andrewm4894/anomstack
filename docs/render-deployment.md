# Deploying Anomstack to Render

This guide covers deploying Anomstack to [Render](https://render.com) using the Blueprint infrastructure-as-code approach.

## Prerequisites

1. **GitHub Repository**: Your Anomstack code must be in a GitHub repository
2. **Render Account**: Create a free account at [render.com](https://render.com)
3. **Render CLI** (optional): Install for command-line management
   ```bash
   # Install via npm
   npm install -g render-cli

   # Or via homebrew (macOS)
   brew install render
   ```

## Quick Start

### 1. Update render.yaml

Edit `render.yaml` and update the repository URL:

```yaml
services:
  - type: web
    runtime: docker
    name: anomstack-demo
    repo: https://github.com/YOUR_USERNAME/anomstack.git  # Update this!
    branch: main
    # ... rest of config
```

### 2. Commit and Push

```bash
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

### 3. Deploy via Render Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **Blueprints** in the left sidebar
3. Click **New Blueprint Instance**
4. Connect your GitHub account (if not already connected)
5. Select your Anomstack repository
6. Render will automatically detect `render.yaml`
7. Click **Apply** to start deployment

### 4. Set Admin Password (Secret)

After deployment starts:

1. Go to your service in the Render Dashboard
2. Click **Environment** in the left sidebar
3. Find `ANOMSTACK_ADMIN_PASSWORD`
4. Click the lock icon to mark it as a secret
5. Set your desired password
6. Click **Save Changes**

The service will automatically redeploy with the secret set.

## Configuration Details

### Service Architecture

The deployment uses a single web service running:
- **Dagster webserver** (port 3000) - Orchestration UI
- **Dagster daemon** - Job scheduling and execution
- **FastHTML dashboard** (port 8080) - Metrics visualization
- **nginx reverse proxy** (port 80) - Routing and authentication

All services run in one container using the `docker/Dockerfile.fly` image.

### Persistent Storage

A 10GB persistent disk is mounted at `/data` for:
- **DuckDB database**: `/data/anomstack.db`
- **ML models**: `/data/models/`

You can increase disk size in render.yaml (but cannot decrease):

```yaml
disk:
  name: anomstack-data
  mountPath: /data
  sizeGB: 20  # Increase as needed
```

### Environment Variables

The `render.yaml` includes all necessary environment variables from the demo profile:
- Core Dagster configuration
- Storage paths
- Enabled/disabled metric batches
- PostHog tracking

You can override any variable in the Render Dashboard under **Environment**.

### Health Checks

The service uses `/nginx-health` endpoint for health monitoring.

### Resource Allocation

Default plan: **Starter** (512MB RAM, 0.5 CPU)

Upgrade in render.yaml if needed:
```yaml
plan: standard  # or pro, pro_plus
```

See [Render pricing](https://render.com/pricing) for plan details.

## Deployment Commands

Using the Makefile:

```bash
# Validate configuration
make render-validate

# Get deployment instructions
make render-deploy

# List all services
make render-services

# View logs (requires RENDER_SERVICE_ID)
export RENDER_SERVICE_ID=srv-xxxxx
make render-logs

# SSH into service
make render-shell
```

## Monitoring and Management

### View Logs

**Via Dashboard:**
1. Go to your service in Render Dashboard
2. Click **Logs** tab
3. View real-time logs from all processes

**Via CLI:**
```bash
# List services to get service ID
render services list

# Tail logs
export RENDER_SERVICE_ID=srv-xxxxx
make render-logs
```

### Access the Application

After deployment completes:

1. **Dashboard** (public): `https://anomstack-demo.onrender.com/`
2. **Dagster** (authenticated): `https://anomstack-demo.onrender.com/dagster`
   - Username: `admin` (or your custom value)
   - Password: Value you set for `ANOMSTACK_ADMIN_PASSWORD`

### SSH Access

```bash
# Get service ID
render services list

# Connect
export RENDER_SERVICE_ID=srv-xxxxx
make render-shell
```

## Customization

### Change Metric Batches

Edit environment variables in `render.yaml` to enable/disable specific metrics:

```yaml
# Disable a metric batch
- key: ANOMSTACK__WEATHER__INGEST_DEFAULT_SCHEDULE_STATUS
  value: STOPPED

# Enable a metric batch
- key: ANOMSTACK__WEATHER__INGEST_DEFAULT_SCHEDULE_STATUS
  value: RUNNING
```

### Add Database Credentials

For production metrics (BigQuery, Snowflake, etc.), add credentials as secrets:

```yaml
envVars:
  - key: BIGQUERY_CREDENTIALS
    sync: false  # Mark as secret

  - key: SNOWFLAKE_PASSWORD
    sync: false
```

Then set values in Render Dashboard under **Environment**.

### Change Region

Available regions: `oregon`, `frankfurt`, `singapore`, `ohio`, `virginia`

```yaml
region: frankfurt  # Change in render.yaml
```

## Cost Optimization

The demo configuration disables high-frequency metric batches to reduce CPU usage:
- Netdata (very high frequency)
- Prometheus (5-minute intervals)

This keeps the deployment running smoothly on the Starter plan.

For production, consider:
1. Upgrading to Standard or Pro plan
2. Enabling only required metric batches
3. Adjusting cron schedules for less frequent ingestion

## Troubleshooting

### Build Failures

Check build logs in Render Dashboard. Common issues:
- Docker build context errors
- Missing dependencies
- Timeout during build

Solution: Review Dockerfile.fly and ensure all COPY paths are correct.

### Health Check Failures

If health checks fail:
1. Check nginx is starting correctly
2. Verify `/nginx-health` endpoint responds
3. Review startup logs for service initialization errors

### Disk Space Issues

Monitor disk usage:
```bash
# SSH into service
make render-shell

# Check disk usage
df -h /data
du -sh /data/*
```

Increase disk size in render.yaml if needed.

### Service Crashes

Check logs for errors:
```bash
make render-logs
```

Common causes:
- Out of memory (upgrade plan)
- Long-running jobs (adjust `ANOMSTACK_MAX_RUNTIME_SECONDS_TAG`)
- Database connection issues

## Migrating from Fly.io

If migrating from Fly.io:

1. **Export data** (if needed):
   ```bash
   # SSH into Fly.io app
   fly ssh console -a your-app

   # Backup DuckDB
   cp /data/anomstack.db /tmp/backup.db

   # Download via SFTP or scp
   ```

2. **Deploy to Render** (follow Quick Start above)

3. **Import data** (if needed):
   ```bash
   # SSH into Render service
   make render-shell

   # Upload backup.db via SFTP
   # Then restore
   cp /tmp/backup.db /data/anomstack.db
   ```

4. **Update DNS** if using custom domain

5. **Decommission Fly.io app** when ready

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render Blueprint Spec](https://render.com/docs/blueprint-spec)
- [Render Persistent Disks](https://render.com/docs/disks)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Anomstack Documentation](https://anomstack.io/docs)

## Support

For issues:
- Render support: [Render Discord](https://render.com/discord)
- Anomstack issues: [GitHub Issues](https://github.com/andrewm4894/anomstack/issues)
