# Render Deployment Setup - Summary

## ✅ What's Been Configured

I've set up complete Render deployment configuration for your Anomstack demo instance. Here's what was created:

### 1. **render.yaml** (Blueprint Configuration)
- Single web service running Docker
- Persistent 10GB disk at `/data` for DuckDB and models
- All demo environment variables configured (same as Fly.io demo profile)
- Health checks using `/nginx-health` endpoint
- Starter plan (512MB RAM, 0.5 CPU) - upgrade as needed

### 2. **Makefile Commands** (Added to existing Makefile)
```bash
make render-validate     # Validate configuration
make render-deploy       # Get deployment instructions
make render-services     # List all services
make render-logs         # View logs
make render-shell        # SSH into service
```

### 3. **Documentation**
- **docs/render-deployment.md**: Complete deployment guide with troubleshooting
- **CLAUDE.md**: Updated with Render deployment commands

## 🚀 Next Steps to Deploy

### Step 1: Update Repository URL
Edit `render.yaml` (line 7) with your GitHub repository URL:
```yaml
repo: https://github.com/YOUR_USERNAME/anomstack.git
```

### Step 2: Commit and Push
```bash
git add render.yaml Makefile CLAUDE.md docs/render-deployment.md RENDER_SETUP.md
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 3: Deploy via Render Dashboard
1. Go to https://dashboard.render.com/blueprints
2. Click **"New Blueprint Instance"**
3. Connect your GitHub account (if not already)
4. Select your Anomstack repository
5. Render will detect `render.yaml` automatically
6. Click **"Apply"** to start deployment

### Step 4: Set Admin Password Secret
After deployment starts:
1. Go to your service in Render Dashboard
2. Navigate to **Environment** tab
3. Find `ANOMSTACK_ADMIN_PASSWORD`
4. Click the lock icon to mark it as a secret
5. Enter your desired admin password
6. Click **"Save Changes"**

The service will automatically redeploy with the secret.

## 📋 What's Deployed

The single web service runs:
- **Dagster webserver** (port 3000) - Orchestration UI
- **Dagster daemon** - Job scheduling and execution
- **FastHTML dashboard** (port 8080) - Metrics visualization
- **nginx reverse proxy** (port 80) - Routing and authentication

## 🌐 Access URLs

After deployment completes (takes 5-10 minutes):

- **Dashboard** (public): `https://anomstack-demo.onrender.com/`
- **Dagster UI** (authenticated): `https://anomstack-demo.onrender.com/dagster`
  - Username: `admin`
  - Password: Your `ANOMSTACK_ADMIN_PASSWORD` value

## 🔧 Configuration Highlights

### Enabled Metric Batches (Demo Profile)
- ✅ GitHub repository metrics
- ✅ Currency exchange rates
- ✅ YFinance stock prices
- ✅ HackerNews stories
- ✅ CoinDesk crypto prices
- ✅ Weather data
- ✅ EirGrid power data
- ✅ PostHog analytics
- ✅ Earthquake data (USGS)
- ✅ ISS location tracking

### Disabled Metric Batches (Too CPU intensive)
- ❌ Netdata system metrics
- ❌ Prometheus metrics
- ❌ Netdata HTTP checks

This configuration keeps the demo running smoothly on the Starter plan while demonstrating diverse data sources.

## 💰 Cost Optimization

The demo configuration is optimized for cost:
- **Starter plan**: ~$7/month for compute
- **10GB disk**: ~$0.25/month
- **Total**: ~$7.25/month

High-frequency metric batches (Netdata, Prometheus) are disabled to reduce CPU usage.

For production:
- Upgrade to Standard or Pro plan for more resources
- Enable only required metric batches
- Adjust cron schedules as needed

## 🔍 Monitoring

### View Logs
```bash
# List services
make render-services

# View logs (replace with your service ID)
export RENDER_SERVICE_ID=srv-xxxxx
make render-logs
```

### SSH Access
```bash
export RENDER_SERVICE_ID=srv-xxxxx
make render-shell
```

### Render Dashboard
- Real-time logs
- Metrics (CPU, memory, bandwidth)
- Deployment history
- Environment variables

## 🆚 Render vs Fly.io

Both platforms work great for Anomstack. Key differences:

| Feature | Render | Fly.io |
|---------|--------|--------|
| **Config** | render.yaml (Blueprint) | fly.toml |
| **Deployment** | Dashboard or CLI | CLI required |
| **Pricing** | Flat monthly rate | Pay-as-you-go |
| **Free tier** | 90 days free | Limited free tier |
| **Regions** | 5 regions | 30+ regions |
| **Dashboard** | Excellent web UI | CLI-focused |

Choose Render if you prefer:
- Infrastructure-as-code with Blueprint YAML
- Predictable monthly pricing
- Excellent web dashboard
- Simpler deployment workflow

## 📚 Additional Resources

- **Deployment Guide**: `docs/render-deployment.md`
- **Render Docs**: https://render.com/docs
- **Blueprint Spec**: https://render.com/docs/blueprint-spec
- **Anomstack Docs**: https://anomstack.io/docs

## ❓ Troubleshooting

### Build fails
Check Dockerfile.fly is correct and all paths exist. Review build logs in Render Dashboard.

### Health checks fail
Verify nginx starts correctly and `/nginx-health` responds. Check startup logs.

### Out of memory
Upgrade to Standard or Pro plan. Adjust `ANOMSTACK_MAX_RUNTIME_SECONDS_TAG` to limit job runtime.

### Need help?
- Check `docs/render-deployment.md` for detailed troubleshooting
- Render support: https://render.com/discord
- Anomstack issues: https://github.com/andrewm4894/anomstack/issues

---

**Ready to deploy?** Follow the 4 steps above and you'll have Anomstack running on Render in ~10 minutes! 🚀
