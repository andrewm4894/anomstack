# Anomstack Fly.io Deployment - Quick Start

**🚀 Live Demo**: https://anomstack-demo.fly.dev

## Current Architecture

- **📊 Public Dashboard**: https://anomstack-demo.fly.dev/ (no authentication)
- **🔐 Protected Dagster**: https://anomstack-demo.fly.dev/dagster (configurable admin credentials)
- **🌐 nginx Reverse Proxy**: Routes and protects services
- **🗄️ Managed PostgreSQL**: Fly.io hosted database
- **📦 Persistent Volume**: 10GB for DuckDB and models

## Quick Deploy

**New! 🎉 Automatic .env Integration**

The deployment script now automatically reads your local `.env` file and sets those variables as Fly secrets!

```bash
# 1. Install Fly CLI and login
fly auth login

# 2. Set up your .env file with your secrets
cp .example.env .env
# Edit .env with your actual values (API keys, passwords, etc.)

# 3. Preview what will be deployed (optional)
./scripts/deployment/preview_fly_secrets.sh

# 4. Deploy (reads .env automatically!)
./scripts/deployment/deploy_fly.sh

# 5. Or deploy with custom app name
./scripts/deployment/deploy_fly.sh my-anomstack-app
```

**What gets deployed:**
- ✅ All non-empty environment variables from your `.env`
- ✅ Automatically skips local-only variables (like `tmpdata` paths)
- ✅ Masks sensitive values in preview mode
- ✅ Sets Fly-specific overrides (paths, database config)
- ✅ Generates secure admin credentials (or uses yours)

**Manual approach (if you prefer):**
```bash
# Old manual way (still works)
fly deploy
fly secrets set ANOMSTACK_ALERT_EMAIL_TO="your@email.com"
```

## Key Files

- `fly.toml` - App configuration
- `nginx.conf` - Reverse proxy with auth
- `docker/Dockerfile.fly` - Multi-service container
- `dagster_fly.yaml` - PostgreSQL Dagster config
- `start.sh` - Service startup script

## Access

- **Dashboard** (Public): https://your-app.fly.dev/
- **Dagster** (Protected): https://your-app.fly.dev/dagster
- **Logs**: `fly logs`
- **SSH**: `fly ssh console`

## Security Model

**nginx handles routing and authentication:**
- `/` → Dashboard (public)
- `/dagster` → Dagster UI (basic auth)
- `/graphql` → Dagster API (basic auth)
- `/_next/*` → Static assets (basic auth)

## Architecture Benefits

✅ **Single VM**: All services in one container  
✅ **No Docker-in-Docker**: Uses DefaultRunLauncher  
✅ **Auto-scaling**: 1-3 instances based on load  
✅ **Global edge**: Deploy close to data sources  
✅ **Managed database**: Automatic backups  
✅ **Simple auth**: Basic auth for admin features  

---

📖 **For detailed documentation**: See [docs/docs/deployment/fly.md](docs/docs/deployment/fly.md) 