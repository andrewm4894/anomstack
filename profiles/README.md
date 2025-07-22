# Anomstack Deployment Profiles

This directory contains deployment profiles that act like "Helm values files" for Anomstack, allowing you to configure different environments without modifying the original metric batch examples.

## How It Works

Deployment profiles leverage Anomstack's existing environment variable override system (`ANOMSTACK__<METRIC_BATCH>__<PARAMETER>`) to enable and configure metric batches at deployment time.

### Benefits

✅ **Keep examples pristine** - Original examples remain as clean templates  
✅ **Environment-specific configs** - Different settings for demo, dev, production  
✅ **Easy deployment** - Apply profiles during deployment with a single flag  
✅ **Source controlled** - All configurations are versioned and visible  
✅ **User-friendly** - Others can easily redeploy your exact demo configuration  
✅ **Hot-reloadable** - Changes to profiles can be applied without restarts  

## Available Profiles

### `demo.env` 
**Purpose**: Configuration for the public demo instance  
**Features**:
- Enables key examples (netdata, weather, hackernews, python_ingest_simple)
- All job schedules running
- Email alerts enabled
- Demo-appropriate settings

### `production.env`
**Purpose**: Production deployment template  
**Features**:
- Disables examples for clean deployment
- Conservative alert thresholds
- Production-grade database paths
- Team-based alert routing

### `development.env`
**Purpose**: Development/staging environments  
**Features**:
- Enables all examples for testing
- More sensitive alert thresholds
- Hot-reload features enabled
- Development-friendly settings

## Usage

### Option 1: Enhanced Deployment Script (Recommended)

```bash
# Deploy with demo profile
./scripts/deployment/deploy_fly.sh --profile demo

# Deploy with production profile  
./scripts/deployment/deploy_fly.sh --profile production

# Deploy with custom profile
./scripts/deployment/deploy_fly.sh --profile my-custom-profile
```

### Option 2: Manual Profile Application

```bash
# Copy profile to .env and deploy
cp profiles/demo.env .env
# Add your secrets to .env
echo "ANOMSTACK_OPENAI_KEY=your-key" >> .env
./scripts/deployment/deploy_fly.sh
```

### Option 3: Profile Merging

```bash
# Start with your base .env
cp .example.env .env
# Edit with your API keys, credentials, etc.
vim .env

# Merge with demo profile for deployment
cat profiles/demo.env >> .env
./scripts/deployment/deploy_fly.sh
```

## Creating Custom Profiles

### 1. Create Profile File

```bash
# Create new profile
vim profiles/my-company.env
```

### 2. Profile Structure

```bash
# Company Production Anomstack Profile
ANOMSTACK_IGNORE_EXAMPLES=yes
ANOMSTACK_TABLE_KEY=company_production.metrics

# Enable your specific metric batches
ANOMSTACK__MY_BUSINESS_METRICS__INGEST_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__MY_BUSINESS_METRICS__TRAIN_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__MY_BUSINESS_METRICS__SCORE_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__MY_BUSINESS_METRICS__ALERT_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__MY_BUSINESS_METRICS__ALERT_METHODS=email,slack
```

### 3. Deploy with Custom Profile

```bash
./scripts/deployment/deploy_fly.sh --profile my-company
```

## Profile Composition

Profiles are applied on top of your base `.env` configuration:

1. **Base `.env`**: Your secrets, API keys, database credentials
2. **Profile**: Environment-specific metric batch enablement and configuration  
3. **Deployment**: Combined configuration deployed as Fly secrets

This layered approach means:
- **Secrets stay in your `.env`** (not committed to source control)
- **Profile configurations are shareable** and source controlled
- **Others can use your exact demo setup** by applying your profile

## Environment Variable Override System

Profiles use Anomstack's built-in override system:

```bash
# Format: ANOMSTACK__<METRIC_BATCH>__<PARAMETER>=<VALUE>
ANOMSTACK__NETDATA__INGEST_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__WEATHER__ALERT_METHODS=email,slack
ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_THRESHOLD=0.7
```

This allows you to:
- Enable/disable specific metric batches
- Customize schedules, alert methods, thresholds
- Override any parameter from `metrics/defaults/defaults.yaml`
- Configure multiple batches consistently

## Examples

### Demo Instance Recreation

Anyone can recreate your exact demo instance:

```bash
git clone https://github.com/andrewm4894/anomstack.git
cd anomstack
cp .example.env .env
# Add their own API keys to .env
./scripts/deployment/deploy_fly.sh --profile demo my-demo-instance
```

### Multi-Environment Deployment

```bash
# Deploy to different environments with different profiles
./scripts/deployment/deploy_fly.sh --profile development anomstack-dev
./scripts/deployment/deploy_fly.sh --profile production anomstack-prod  
./scripts/deployment/deploy_fly.sh --profile demo anomstack-demo
```

### Custom Company Setup

```bash
# Create company-specific profile
cat > profiles/acme-corp.env << EOF
ANOMSTACK_IGNORE_EXAMPLES=yes
ANOMSTACK_TABLE_KEY=acme.anomaly_detection.metrics
ANOMSTACK__ACME_SALES_METRICS__INGEST_DEFAULT_SCHEDULE_STATUS=RUNNING
ANOMSTACK__ACME_USER_METRICS__INGEST_DEFAULT_SCHEDULE_STATUS=RUNNING
EOF

# Deploy with company profile
./scripts/deployment/deploy_fly.sh --profile acme-corp acme-anomstack
```

## Next Steps

To implement profile support in the deployment script, see the enhancement in `scripts/deployment/deploy_fly.sh` that adds the `--profile` flag. 