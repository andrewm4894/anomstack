---
description: Debug the Anomstack demo instance on Fly.io - check schedules, jobs, LLM alerts, and PostHog tracking
user_invocable: true
---

# Debug Demo Instance

This skill helps diagnose issues with the Anomstack demo instance running on Fly.io (app: `anomstack-demo`).

## Quick Checks

### 1. Check Fly.io App Status
```bash
fly status -a anomstack-demo
fly logs -a anomstack-demo --no-tail | tail -50
```

### 2. List Fly.io Secrets
```bash
fly secrets list -a anomstack-demo
```

### 3. Check Dagster Schedule Status
SSH into the instance and list schedules:
```bash
fly ssh console -a anomstack-demo -C "sh -c 'cd /opt/dagster/app && dagster schedule list -m anomstack.main 2>&1'" | grep -i llmalert
```

### 4. Check Recent LLM Alert Runs
Query the Dagster run database:
```bash
fly ssh console -a anomstack-demo -C "python3 -c \"
import sqlite3
conn = sqlite3.connect('/data/dagster_storage/history/runs/index.db')
cur = conn.cursor()
cur.execute('''SELECT DISTINCT run_id, datetime(timestamp) FROM event_logs WHERE event LIKE \\\"%llmalert%\\\" ORDER BY timestamp DESC LIMIT 10''')
for row in cur.fetchall():
    print(row)
\""
```

### 5. Check a Specific Run's Status
Replace `<run_id>` with the actual run ID:
```bash
fly ssh console -a anomstack-demo -C "python3 -c \"
import sqlite3
conn = sqlite3.connect('/data/dagster_storage/history/runs/<run_id>.db')
cur = conn.cursor()
cur.execute('SELECT dagster_event_type, datetime(timestamp) FROM event_logs ORDER BY timestamp DESC LIMIT 10')
for row in cur.fetchall():
    print(row)
\""
```

### 6. Check LLM Alert Job Output
Check the result of the llmalert step:
```bash
fly ssh console -a anomstack-demo -C "python3 -c \"
import pickle
with open('/data/artifacts/storage/<run_id>/<batch>_llmalert/result', 'rb') as f:
    df = pickle.load(f)
print('Shape:', df.shape)
print('Columns:', list(df.columns))
if len(df) > 0:
    print(df.head())
else:
    print('DataFrame is empty - no anomalies detected')
\""
```

### 7. Test anomaly-agent Directly
Verify the LLM is working:
```bash
fly ssh console -a anomstack-demo -C "python3 -c \"
import pandas as pd
from anomaly_agent import AnomalyAgent

dates = pd.date_range(start='2026-01-01', periods=10, freq='h')
values = [10, 11, 10, 9, 10, 100, 10, 11, 9, 10]  # 100 is obvious anomaly
df = pd.DataFrame({'metric_timestamp': dates, 'metric_value': values})

agent = AnomalyAgent()
anomalies = agent.detect_anomalies(df, timestamp_col='metric_timestamp')
df_anomalies = agent.get_anomalies_df(anomalies)
print(f'Detected {len(df_anomalies)} anomalies')
print(df_anomalies)
\""
```

### 8. Check Environment Variables
```bash
fly ssh console -a anomstack-demo -C "python3 -c \"
import os
print('OPENAI_API_KEY set:', 'OPENAI_API_KEY' in os.environ)
print('ANOMSTACK_LLM_PLATFORM:', os.environ.get('ANOMSTACK_LLM_PLATFORM', 'not set'))
print('ANOMSTACK_OPENAI_MODEL:', os.environ.get('ANOMSTACK_OPENAI_MODEL', 'not set'))
print('POSTHOG_ENABLED:', os.environ.get('POSTHOG_ENABLED', 'not set'))
\""
```

### 9. Check PostHog Python Package
```bash
fly ssh console -a anomstack-demo -C "python3 -c \"
try:
    import posthog
    print(f'posthog version: {posthog.VERSION}')
except ImportError:
    print('posthog NOT installed - LLM tracking to PostHog will not work')
\""
```

### 10. Check Disk Usage
```bash
fly ssh console -a anomstack-demo -C "df -h"
fly ssh console -a anomstack-demo -C "du -sh /data/*"
```

## PostHog Checks

Use the PostHog MCP tools to check LLM event tracking:

1. Switch to the correct project:
```
mcp__posthog__switch-project with projectId: 148051
```

2. Check LLM event definitions:
```
mcp__posthog__event-definitions-list with q: "llm"
```

3. Check LLM costs:
```
mcp__posthog__get-llm-total-costs-for-project with projectId: 148051, days: 30
```

## Common Issues

### LLM Alerts Not Sending Events to PostHog
- **Cause**: `posthog` Python package not installed
- **Fix**: Add `posthog` to requirements.txt and redeploy

### LangSmith Authentication Errors
- **Cause**: Invalid/expired LANGSMITH_API_KEY
- **Impact**: Tracing won't work, but LLM calls still succeed
- **Fix**: Update the LANGSMITH_API_KEY secret or disable tracing

### LLM Alert Jobs Return Empty Results
- **Cause**: The LLM may not detect anomalies in the data
- **Check**: Verify input data has actual anomalies to detect
- **Debug**: Check the `get_llmalert_data` step output to see what data was passed to the LLM

### Schedules Show RUNNING but Jobs Don't Execute
- **Check**: Verify the Dagster daemon is running
- **Check**: Look for run timeouts or resource constraints

## Deployment

After fixing issues, redeploy:
```bash
make fly-deploy-demo
```

For a fresh build (clears Docker cache):
```bash
make fly-deploy-demo-fresh
```

## Key Paths on Fly.io Instance

- App directory: `/opt/dagster/app/`
- Data volume: `/data/`
- DuckDB database: `/data/anomstack.db`
- Dagster storage: `/data/dagster_storage/`
- Compute logs: `/data/artifacts/storage/`
