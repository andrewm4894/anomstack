#!/usr/bin/env python3
"""
Test script to demonstrate the new environment variable override functionality.
"""

import os
import sys
from pathlib import Path

# Add the anomstack directory to the path
sys.path.insert(0, str(Path(__file__).parent / "anomstack"))

from config import get_specs

def test_config_overrides():
    """Test the new environment variable override functionality."""
    
    print("Testing metric batch-specific environment variable overrides...")
    print("=" * 60)
    
    # First, get specs without environment variables to see original values
    print("Original values (without environment variables):")
    specs_original = get_specs("./metrics")
    if "python_ingest_simple" in specs_original:
        batch_spec = specs_original["python_ingest_simple"]
        print(f"  DB: {batch_spec.get('db')}")
        print(f"  Alert methods: {batch_spec.get('alert_methods')}")
        print(f"  Ingest cron schedule: {batch_spec.get('ingest_cron_schedule')}")
        print(f"  Table key: {batch_spec.get('table_key')}")
    print()
    
    # Set up test environment variables
    print("Setting environment variables:")
    os.environ["ANOMSTACK__PYTHON_INGEST_SIMPLE__DB"] = "bigquery"
    os.environ["ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_METHODS"] = "email"
    os.environ["ANOMSTACK__PYTHON_INGEST_SIMPLE__INGEST_CRON_SCHEDULE"] = "*/1 * * * *"
    print("  ANOMSTACK__PYTHON_INGEST_SIMPLE__DB=bigquery")
    print("  ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_METHODS=email")
    print("  ANOMSTACK__PYTHON_INGEST_SIMPLE__INGEST_CRON_SCHEDULE=*/1 * * * *")
    print()
    
    # Get the specs with environment variables
    print("Values after environment variable overrides:")
    specs = get_specs("./metrics")
    
    # Check if python_ingest_simple batch exists
    if "python_ingest_simple" in specs:
        batch_spec = specs["python_ingest_simple"]
        print(f"  DB (should be 'bigquery'): {batch_spec.get('db')}")
        print(f"  Alert methods (should be 'email'): {batch_spec.get('alert_methods')}")
        print(f"  Ingest cron schedule (should be '*/1 * * * *'): {batch_spec.get('ingest_cron_schedule')}")
        print(f"  Table key (should be from YAML): {batch_spec.get('table_key')}")
        
        # Verify the overrides worked
        print()
        print("Verification:")
        print(f"  DB override worked: {batch_spec.get('db') == 'bigquery'}")
        print(f"  Alert methods override worked: {batch_spec.get('alert_methods') == 'email'}")
        print(f"  Cron schedule override worked: {batch_spec.get('ingest_cron_schedule') == '*/1 * * * *'}")
    else:
        print("python_ingest_simple batch not found in specs")
    
    # Clean up environment variables
    del os.environ["ANOMSTACK__PYTHON_INGEST_SIMPLE__DB"]
    del os.environ["ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_METHODS"]
    del os.environ["ANOMSTACK__PYTHON_INGEST_SIMPLE__INGEST_CRON_SCHEDULE"]
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_config_overrides() 