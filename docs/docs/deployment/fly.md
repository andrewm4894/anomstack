---
sidebar_position: 3
---

# Fly.io Deployment

Deploy Anomstack to Fly.io for a production-ready, scalable anomaly detection platform in the cloud.

:::tip Live Demo
🚀 **See it in action**: [https://anomstack-demo.fly.dev](https://anomstack-demo.fly.dev)

- **📊 Public Dashboard**: Try the Anomstack interface (no login required)
- **🔐 Admin Interface**: [/dagster](https://anomstack-demo.fly.dev/dagster) (configurable admin credentials)
:::

## Overview

[Fly.io](https://fly.io/) is a modern cloud platform that runs your applications close to your users. This deployment gives you:

- **🌐 Public Demo Interface**: Shareable anomaly detection dashboard
- **🔐 Protected Admin UI**: Secure access to orchestration controls
- **📡 Global Edge Deployment**: Run close to your data sources worldwide
- **⚡ Auto-scaling**: Scale up/down based on demand
- **🗄️ Managed PostgreSQL**: Fully managed database with automatic backups  
- **📦 Persistent Volumes**: Reliable storage for metrics and models
- **💰 Simple Pricing**: Pay only for what you use

## Architecture

Our Fly.io deployment uses **nginx reverse proxy** with **authentication-based routing**:

```mermaid
graph TB
    subgraph "Public Internet"
        USERS[👥 Users]
        ADMIN[🔐 Admin Users]
    end
    
    subgraph "Fly.io Edge (nginx)"
        PROXY[nginx Reverse Proxy<br/>Port 80/443]
    end
    
    subgraph "Fly.io VM Container"
        DASH[📊 Dashboard<br/>Port 8080<br/><i>Public</i>]
        WEB[⚙️ Dagster Webserver<br/>Port 3000<br/><i>Protected</i>]
        DAEMON[🔄 Dagster Daemon<br/>Background Jobs]
        CODE[📦 Code Server<br/>Port 4000<br/>Internal]
    end
    
    subgraph "Fly.io Services"
        PG[(🗄️ Managed PostgreSQL)]
        VOL[📦 Persistent Volume<br/>10GB]
    end
    
    USERS --> PROXY
    ADMIN --> PROXY
    PROXY -->|"/ (no auth)"| DASH
    PROXY -->|"/dagster (basic auth)"| WEB
    WEB --> CODE
    DAEMON --> CODE
    WEB --> PG
    DAEMON --> PG
    CODE --> VOL
```

### Security Model

**nginx handles all routing and authentication:**

| Path | Access | Target | Description |
|------|---------|--------|-------------|
| `/` | 🌐 **Public** | Dashboard (8080) | Anomaly detection interface |
| `/dagster` | 🔐 **Protected** | Webserver (3000) | Orchestration controls |
| `/graphql` | 🔐 **Protected** | Webserver (3000) | Dagster API endpoints |
| `/_next/*` | 🔐 **Protected** | Webserver (3000) | Static assets |

**Authentication**: Basic HTTP Auth (configurable via environment variables, defaults to `admin` / `anomstack2024`)

## Prerequisites

1. **Fly.io Account**: Sign up at [fly.io](https://fly.io)
2. **Fly CLI**: Install the Fly.io CLI tool
3. **Git**: For cloning the repository

### Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux/WSL
curl -L https://fly.io/install.sh | sh

# Windows
iwr https://fly.io/install.ps1 -useb | iex
```

### Login to Fly.io

```bash
fly auth login
```

## Quick Deployment

The fastest way to get your own Anomstack instance:

### 1. Clone Repository

```bash
git clone https://github.com/andrewm4894/anomstack.git
cd anomstack
```

### 2. Set Up Environment Variables

**New! 🎉 Automatic .env Integration**

```bash
# Copy example environment file
cp .example.env .env

# Edit with your actual values
nano .env  # or vim .env, code .env, etc.
```

**Example .env file:**
```bash
# Your actual secrets
ANOMSTACK_ALERT_EMAIL_FROM=alerts@mycompany.com
ANOMSTACK_ALERT_EMAIL_TO=team@mycompany.com
ANOMSTACK_ALERT_EMAIL_PASSWORD=my-gmail-app-password

ANOMSTACK_SLACK_BOT_TOKEN=xoxb-your-slack-token
ANOMSTACK_SLACK_CHANNEL=#anomalies

ANOMSTACK_OPENAI_KEY=sk-your-openai-key

# Custom admin credentials
ANOMSTACK_ADMIN_USERNAME=myadmin
ANOMSTACK_ADMIN_PASSWORD=super-secure-password-123

# Database connections
ANOMSTACK_SNOWFLAKE_ACCOUNT=my-account
ANOMSTACK_SNOWFLAKE_USER=anomstack_user
ANOMSTACK_SNOWFLAKE_PASSWORD=my-snowflake-password
```

### 3. Preview Deployment (Optional)

```bash
# See what environment variables will be set as Fly secrets
./scripts/deployment/preview_fly_secrets.sh
```

This shows you:
- ✅ **Variables that WILL be deployed** (API keys, passwords, etc.)
- 🏠 **Variables that will be SKIPPED** (local development paths)
- 🔒 **Fly-specific overrides** that will be applied
- 🔐 **Admin credentials** that will be generated

### 4. Deploy

```bash
# Deploy with automatic .env reading
./scripts/deployment/deploy_fly.sh

# Or specify your own app name
./scripts/deployment/deploy_fly.sh my-company-anomstack
```

### 5. Access Your Instance

After deployment completes:
- **📊 Dashboard**: `https://your-app-name.fly.dev/`
- **🔐 Admin UI**: `https://your-app-name.fly.dev/dagster` (credentials shown after deploy)

## Manual Deployment

For more control over the deployment process:

### 1. Create Fly.io App

```bash
# Replace 'my-anomstack' with your preferred app name
fly apps create my-anomstack
```

### 2. Set Up Database

```bash
# Create PostgreSQL cluster
fly postgres create --name my-anomstack-db --region ord

# Attach to your app (creates DATABASE_URL secret automatically)
fly postgres attach my-anomstack-db -a my-anomstack
```

### 3. Create Persistent Volume

```bash
# Create 10GB volume for metrics data
fly volumes create anomstack_data --region ord --size 10 -a my-anomstack
```

### 4. Configure Secrets (Optional)

Set up alerts and integrations:

```bash
# Email alerts
fly secrets set \
  ANOMSTACK_ALERT_EMAIL_FROM="alerts@yourcompany.com" \
  ANOMSTACK_ALERT_EMAIL_TO="team@yourcompany.com" \
  ANOMSTACK_ALERT_EMAIL_PASSWORD="your-app-password" \
  -a my-anomstack

# Slack alerts
fly secrets set \
  ANOMSTACK_SLACK_BOT_TOKEN="xoxb-your-token" \
  ANOMSTACK_SLACK_CHANNEL="#anomalies" \
  -a my-anomstack

# OpenAI integration (for LLM-powered alerts)
fly secrets set \
  ANOMSTACK_OPENAI_KEY="sk-your-api-key" \
  -a my-anomstack
```

### 5. Deploy

```bash
fly deploy -a my-anomstack
```

## Configuration Files

Our deployment uses several key configuration files:

### `fly.toml` - App Configuration

```toml
app = "my-anomstack"
primary_region = "ord"

# Single container with startup script
[[services]]
  protocol = "tcp"
  internal_port = 80  # nginx proxy port

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[mounts]
  destination = "/data"
  source = "anomstack_data"

[vm]
  memory = "2048"
  cpu_kind = "shared"
  cpus = 1
```

### `nginx.conf` - Reverse Proxy with Auth

Key features:
- **Public routing** for dashboard at `/`
- **Protected routing** for Dagster at `/dagster`
- **Basic authentication** for admin features
- **WebSocket support** for real-time updates

### `dagster_fly.yaml` - PostgreSQL Configuration

Configured for:
- **DATABASE_URL** from Fly.io PostgreSQL
- **DefaultRunLauncher** (no Docker dependency)
- **Persistent storage** on mounted volume

## Customizing Your Deployment

### Change Admin Credentials

**Recommended Method - Using Fly Secrets (Secure):**

```bash
# Set custom admin credentials via Fly secrets
fly secrets set \
  ANOMSTACK_ADMIN_USERNAME="youradmin" \
  ANOMSTACK_ADMIN_PASSWORD="your-secure-password-123" \
  -a my-anomstack

# Restart the app to apply changes
fly deploy -a my-anomstack
```

**Alternative Method - Via SSH (temporary):**

```bash
# SSH into your app
fly ssh console -a my-anomstack

# Update password (temporary until next deployment)
htpasswd -bc /etc/nginx/.htpasswd admin newpassword

# Restart nginx
pkill nginx && nginx -g "daemon off;" > /tmp/nginx.log 2>&1 &
```

### Add Custom Metrics

After deployment, add your metric configurations:

1. **SSH into your app:**
   ```bash
   fly ssh console -a my-anomstack
   ```

2. **Create metric configuration:**
   ```bash
   cd /opt/dagster/app/metrics/
   nano my_metrics.yaml
   ```

3. **Add your configuration:**
   ```yaml
   metric_batch: 'my_company_metrics'
   ingest_sql: |
     SELECT 
       CURRENT_TIMESTAMP as metric_timestamp,
       'revenue' as metric_name,
       daily_revenue as metric_value
     FROM my_table
     WHERE date = CURRENT_DATE
   
   data_source: 'bigquery'  # or your data source
   schedule: "0 9 * * *"    # Daily at 9 AM
   ```

4. **Hot reload configuration:**
   ```bash
   python scripts/reload_config.py
   ```

### Scale Your Deployment

```bash
# Scale to multiple instances
fly scale count 2 -a my-anomstack

# Increase memory
fly scale memory 4096 -a my-anomstack

# Upgrade to dedicated CPU
fly scale vm dedicated-cpu-1x -a my-anomstack
```

## Monitoring & Maintenance

### View Application Logs

```bash
# All services
fly logs -a my-anomstack

# Follow logs in real-time
fly logs -a my-anomstack -f

# Specific log files via SSH
fly ssh console -a my-anomstack
tail -f /tmp/webserver.log
tail -f /tmp/dashboard.log
tail -f /tmp/nginx.log
```

### Health Monitoring

```bash
# Check status
fly status -a my-anomstack

# View metrics
fly metrics -a my-anomstack

# Test endpoints
curl -I https://your-app.fly.dev/           # Dashboard (public)
curl -I https://your-app.fly.dev/dagster    # Should get 401
curl -I -u admin:anomstack2024 https://your-app.fly.dev/dagster  # Should get 200
```

### Database Management

```bash
# Connect to database
fly postgres connect -a my-anomstack-db

# View database status
fly status -a my-anomstack-db

# Create backup
fly postgres backup my-anomstack-db
```

## Storage & Data Management

### Persistent Volumes

Your data persists across deployments in the mounted volume:

```bash
# View volume usage
fly ssh console -a my-anomstack -c "df -h /data"

# List volumes
fly volumes list -a my-anomstack

# Extend volume size
fly volumes extend <volume-id> --size 20 -a my-anomstack
```

### Data Backup

```bash
# Backup DuckDB database
fly ssh console -a my-anomstack
cp /data/anomstack.db /tmp/backup.db
# Download via scp or upload to cloud storage

# Backup model files
tar -czf /tmp/models_backup.tar.gz /data/models/
```

## Cost Optimization

### Resource Planning

Typical monthly costs for different workloads:

| Workload | Memory | CPU | Storage | PostgreSQL | Est. Cost/Month* |
|----------|--------|-----|---------|------------|-----------------|
| **Light** (10 metrics) | 1GB | shared-cpu-1x | 10GB | 1 CPU | $15-25 |
| **Medium** (100 metrics) | 2GB | shared-cpu-2x | 25GB | 1 CPU | $35-50 |
| **Heavy** (1000+ metrics) | 4GB | dedicated-cpu-1x | 100GB | 2 CPU | $75-120 |

*Estimates based on Fly.io pricing. Check [fly.io/docs/about/pricing](https://fly.io/docs/about/pricing/) for current rates.

### Optimization Tips

1. **Start small**: Begin with 1GB RAM and scale up as needed
2. **Monitor usage**: Use `fly metrics` to track resource consumption
3. **Optimize schedules**: Reduce frequency for less critical metrics
4. **Use efficient queries**: Optimize your metric ingestion SQL
5. **Clean up data**: Regularly archive old metrics if not needed

## Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check startup logs
fly logs -a my-anomstack

# Check individual service logs
fly ssh console -a my-anomstack
cat /tmp/webserver.log
cat /tmp/daemon.log
cat /tmp/dashboard.log
cat /tmp/nginx.log
```

#### Authentication Not Working

```bash
# Test auth manually
curl -I https://your-app.fly.dev/dagster  # Should return 401
curl -I -u admin:anomstack2024 https://your-app.fly.dev/dagster  # Should return 200

# Check nginx config
fly ssh console -a my-anomstack
cat /etc/nginx/.htpasswd
nginx -t  # Test configuration
```

#### Database Connection Issues

```bash
# Test DATABASE_URL
fly ssh console -a my-anomstack
echo $DATABASE_URL
python -c "
from sqlalchemy import create_engine
engine = create_engine('$DATABASE_URL')
print('Database connection successful!')
"
```

#### Volume/Storage Issues

```bash
# Check disk usage
fly ssh console -a my-anomstack
df -h

# Check volume mounts
mount | grep /data

# Test DuckDB access
python -c "
import duckdb
conn = duckdb.connect('/data/anomstack.db')
print('DuckDB connection successful!')
"
```

### Performance Issues

1. **High Memory Usage**: Scale up with `fly scale memory 4096`
2. **Slow Queries**: Optimize your metric ingestion SQL
3. **Database Bottlenecks**: Upgrade PostgreSQL instance
4. **Network Issues**: Consider multi-region deployment

## Advanced Configuration

### Multi-Region Deployment

Deploy globally for better performance:

```toml
# fly.toml
[scaling]
  regions = ["ord", "lhr", "nrt"]  # Chicago, London, Tokyo
  min_machines_running = 1
  max_machines_running = 5
```

### Custom Domains

```bash
# Add custom domain
fly certs create anomalies.yourcompany.com -a my-anomstack

# Verify DNS configuration
fly certs show anomalies.yourcompany.com -a my-anomstack
```

### External Data Sources

Configure connections to your data sources:

```bash
# BigQuery
fly secrets set GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account"...}' -a my-anomstack

# Snowflake
fly secrets set \
  ANOMSTACK_SNOWFLAKE_ACCOUNT="your-account" \
  ANOMSTACK_SNOWFLAKE_USERNAME="your-username" \
  ANOMSTACK_SNOWFLAKE_PASSWORD="your-password" \
  -a my-anomstack

# AWS (for S3 or other services)
fly secrets set \
  AWS_ACCESS_KEY_ID="your-key" \
  AWS_SECRET_ACCESS_KEY="your-secret" \
  -a my-anomstack
```

## Migration Guide

### From Docker Compose

1. **Export your data:**
   ```bash
   # Backup DuckDB and configs
   docker cp anomstack_code_1:/opt/dagster/app/data/anomstack.db ./backup.db
   docker cp anomstack_code_1:/opt/dagster/app/metrics/ ./metrics_backup/
   ```

2. **Deploy to Fly.io:**
   ```bash
   fly deploy
   ```

3. **Upload your data:**
   ```bash
   fly ssh console -a my-anomstack
   # Upload backup.db to /data/
   # Upload metric configs to /opt/dagster/app/metrics/
   ```

4. **Reload configuration:**
   ```bash
   python scripts/reload_config.py
   ```

### From Other Platforms

The same general approach works:
1. Export data and configuration
2. Deploy to Fly.io
3. Import data via SSH
4. Test and verify

## Next Steps

After successful deployment:

1. **🔧 Configure Metrics**: Add your custom metric batches
2. **📧 Set Up Alerts**: Configure email/Slack notifications  
3. **📊 Monitor Performance**: Use Fly.io metrics and Dagster UI
4. **⚡ Scale as Needed**: Adjust resources based on usage
5. **🔒 Security**: Update default passwords and review access
6. **📖 Documentation**: Document your specific metric configurations

## Related Resources

- **📁 Quick Reference**: [fly.md](https://github.com/andrewm4894/anomstack/blob/main/fly.md) in repository root
- **🌐 Fly.io Docs**: [fly.io/docs](https://fly.io/docs)
- **💬 Community**: [community.fly.io](https://community.fly.io)
- **🐛 Issues**: [GitHub Issues](https://github.com/andrewm4894/anomstack/issues)
- **📧 Alerts Setup**: [Email Configuration](../features/alerts.md)
- **💬 Slack Setup**: [Slack Integration](../features/alerts.md)

:::info Questions?
Join our [GitHub Discussions](https://github.com/andrewm4894/anomstack/discussions) or file an issue for deployment help!
::: 

## Smart Environment Variable Management

The deployment script intelligently handles your `.env` file with smart filtering:

### 🧠 Automatic Filtering

**Variables that are SKIPPED (local development only):**
- `ANOMSTACK_DUCKDB_PATH=tmpdata/...` - Local file paths
- `ANOMSTACK_SQLITE_PATH=tmpdata/...` - Local file paths  
- `ANOMSTACK_MODEL_PATH=./tmp/...` - Local model storage
- `ANOMSTACK_HOME=.` - Current directory reference
- `ANOMSTACK_POSTGRES_FORWARD_PORT` - Local port forwarding
- `DAGSTER_CODE_SERVER_HOST=anomstack_code` - Docker Compose specific
- `ANOMSTACK_DASHBOARD_PORT` - Local dashboard port

**Variables that are DEPLOYED:**
- API keys and tokens (OpenAI, Anthropic, etc.)
- Email and Slack credentials
- Database connection strings
- Admin authentication settings
- Alert configuration
- Cloud storage credentials

### 🔒 Fly.io Overrides

These values are automatically set for Fly.io deployment (regardless of your `.env`):

```bash
DAGSTER_HOME="/opt/dagster/dagster_home"
DAGSTER_CODE_SERVER_HOST="localhost"
ANOMSTACK_DUCKDB_PATH="/data/anomstack.db"           # Persistent volume
ANOMSTACK_MODEL_PATH="local:///data/models"          # Persistent volume  
ANOMSTACK_TABLE_KEY="metrics"                        # Simplified table key
ANOMSTACK_IGNORE_EXAMPLES="no"                       # Enable examples
PYTHONPATH="/opt/dagster/app"                        # Container path
```

### 🔐 Security Features

- **Sensitive values are masked** in preview mode (`***MASKED***`)
- **Secrets are set via Fly's secure secret management** (not environment variables)
- **Admin credentials are generated securely** (random password if not provided)
- **Local-only variables are never sent** to the cloud

### 💡 Usage Examples

```bash
# Preview what will be deployed
./scripts/deployment/preview_fly_secrets.sh

# Example output:
# ✅ 8 variables will be set as Fly secrets:
#   ANOMSTACK_ALERT_EMAIL_FROM=alerts@company.com
#   ANOMSTACK_ALERT_EMAIL_TO=team@company.com
#   ANOMSTACK_ALERT_EMAIL_PASSWORD=***MASKED***
#   ANOMSTACK_OPENAI_KEY=***MASKED***
#   ...
#
# 🏠 4 variables will be SKIPPED (local development only):
#   ANOMSTACK_DUCKDB_PATH
#   ANOMSTACK_DASHBOARD_PORT
#   ...
``` 