#!/usr/bin/env python3
"""
Test script to verify anomaly-agent PostHog integration.
Run this on the Fly.io instance to check if LLM events are emitted to PostHog.
"""
import os
import sys

# Print environment info
print("=" * 60)
print("Environment Check")
print("=" * 60)
print(f"POSTHOG_ENABLED: {os.getenv('POSTHOG_ENABLED')}")
print(f"POSTHOG_API_KEY set: {bool(os.getenv('POSTHOG_API_KEY'))}")
print(f"POSTHOG_HOST: {os.getenv('POSTHOG_HOST')}")
print(f"POSTHOG_DISTINCT_ID: {os.getenv('POSTHOG_DISTINCT_ID')}")
print(f"OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")

# Check anomaly-agent version
try:
    import anomaly_agent
    print(f"anomaly-agent version: {anomaly_agent.__version__}")
except Exception as e:
    print(f"anomaly-agent import error: {e}")

# Check posthog version
try:
    import posthog
    print(f"posthog version: {posthog.VERSION}")
except Exception as e:
    print(f"posthog import error: {e}")

# Check posthog callback handler
try:
    from posthog import Posthog
    from posthog.ai.langchain import CallbackHandler
    print("PostHog CallbackHandler import: OK")
except ImportError as e:
    print(f"PostHog CallbackHandler import error: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("Running Anomaly Agent Test")
print("=" * 60)

import pandas as pd
from anomaly_agent import AnomalyAgent

# Create test data with an obvious anomaly
dates = pd.date_range(start='2026-01-01', periods=20, freq='h')
values = [10, 11, 10, 9, 10, 11, 10, 9, 10, 11,
          500,  # Obvious anomaly
          10, 11, 10, 9, 10, 11, 10, 9, 10]

df = pd.DataFrame({
    'metric_timestamp': dates,
    'metric_value': values
})

print(f"Test data shape: {df.shape}")
print(f"Test data values: {values}")
print()

# Run the agent
print("Initializing AnomalyAgent...")
agent = AnomalyAgent()

print("Running detect_anomalies...")
try:
    anomalies = agent.detect_anomalies(df, timestamp_col='metric_timestamp')
    df_anomalies = agent.get_anomalies_df(anomalies)

    print()
    print("=" * 60)
    print("Results")
    print("=" * 60)
    print(f"Detected {len(df_anomalies)} anomalies")
    if len(df_anomalies) > 0:
        print(df_anomalies)
    else:
        print("No anomalies detected (this is unexpected with the test data)")

    print()
    print("SUCCESS: Agent ran successfully.")
    print("Check PostHog LLM Analytics for the trace.")

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
