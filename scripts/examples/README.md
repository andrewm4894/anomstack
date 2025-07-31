# Example Scripts

This directory contains example scripts and testing utilities to help you validate integrations, test functionality, and learn how to work with Anomstack.

## Scripts

### `run_example.py` (Unified Example Runner)
**Minimal wrapper around existing Anomstack infrastructure** to run any example with a clean command-line interface.

**Purpose:**
- Single script to run all Anomstack examples using existing infrastructure
- Uses the same execution path as production Dagster jobs (`get_specs()`, `render()`, `run_df_fn()`)
- Automatic discovery of all examples from metrics directory
- Consistent interface and error handling
- Easy discoverability of available examples

**Available Examples (26 total):**

**🐍 Python Examples (16 - ingest_fn):**
- 🔥 **hackernews** - HackerNews top stories metrics
- ₿ **bitcoin_price** - Current Bitcoin price from Coindesk API
- 📊 **posthog** - PostHog analytics (requires credentials)
- 🌍 **earthquake** - USGS earthquake activity data
- 🚀 **iss_location** - Real-time International Space Station coordinates
- 💱 **currency** - Currency exchange rates
- ⚡ **eirgrid** - Irish electricity grid data
- 🐙 **github** - GitHub repository metrics
- 🌡️ **weather** - Weather data
- 📈 **yfinance** - Financial market data
- 🖥️ **netdata** - System monitoring metrics
- 🔍 **prometheus** - Prometheus metrics
- 🗺️ **tomtom** - Traffic and navigation data
- And more...

**🗄️ SQL Examples (10 - ingest_sql):**
- Various database and data warehouse examples

**Usage:**
```bash
# List all available examples
python scripts/examples/run_example.py --list
make list-examples

# Run a specific example
python scripts/examples/run_example.py hackernews
python scripts/examples/run_example.py bitcoin_price
python scripts/examples/run_example.py posthog
python scripts/examples/run_example.py earthquake
python scripts/examples/run_example.py iss_location

# Using Makefile (new unified approach)
make run-example EXAMPLE=hackernews
make run-example EXAMPLE=bitcoin_price
make run-example EXAMPLE=posthog
make run-example EXAMPLE=earthquake
make run-example EXAMPLE=iss_location

# Legacy Makefile commands (still work)
make hackernews-example  # → run-example EXAMPLE=hackernews
make bitcoin-example     # → run-example EXAMPLE=bitcoin_price  
make posthog-example     # → run-example EXAMPLE=posthog
```

**Help and Options:**
```bash
# Show help
python scripts/examples/run_example.py --help

# List examples
python scripts/examples/run_example.py --list
```

**Architecture & How It Works:**

This script is a minimal wrapper around Anomstack's existing infrastructure:

1. **Uses `get_specs("./metrics")`** - Same config loading as production
2. **Uses `render("ingest_fn", spec)`** - Same Jinja template rendering as production  
3. **Uses `run_df_fn("ingest", rendered_fn)`** - Same function execution as production Dagster jobs

This ensures the script executes examples **exactly** like they run in production, providing reliable testing.

**Sample Output:**
```
📊 Running earthquake example...
==================================================
✅ Example completed successfully!

📊 Results from earthquake:
------------------------------
🔸 earthquake_count_last_day: 338.0
🔸 earthquake_max_magnitude_last_day: 6.2
🔸 earthquake_avg_magnitude_last_day: 2.30

⏱️  Timestamp: 2025-07-31 17:12:22.077753+00:00
📈 Total metrics collected: 3
```

**Environment Variables for PostHog:**
- `POSTHOG_API_KEY` - Your PostHog API key
- `POSTHOG_PROJECT_ID` - Your PostHog project ID
- Other PostHog-specific configuration variables

**Note on Example Import Pattern:**
Examples must have imports **inside** the ingest function (not at module level) to work with `exec()` execution:

```python
# ✅ Correct pattern
def ingest():
    import pandas as pd
    import requests
    # function code...

# ❌ Won't work with run_example.py
import requests
def ingest():
    # function code...
```


## Purpose of Example Scripts

Example scripts serve several important purposes:

### **Integration Testing**
- Validate external service connections
- Test API credentials and permissions
- Verify data pipeline functionality
- Ensure proper configuration setup

### **Learning and Development**
- Provide working examples of integration patterns
- Demonstrate best practices for data ingestion
- Show proper error handling and logging
- Illustrate configuration management

### **Troubleshooting**
- Quick validation of service connectivity
- Debugging integration issues
- Testing configuration changes
- Verifying data quality and format

### **Documentation**
- Live examples of working integrations
- Reference implementations for new integrations
- Code samples for documentation

## Common Use Cases

### **Example Validation**
```bash
# List all available examples (26 total)
make list-examples

# Test individual examples (new unified approach)
make run-example EXAMPLE=hackernews     # HackerNews stories (no credentials)
make run-example EXAMPLE=bitcoin_price  # Bitcoin price (no credentials)
make run-example EXAMPLE=earthquake     # USGS earthquake data (no credentials)
make run-example EXAMPLE=iss_location   # Space station location (no credentials)
make run-example EXAMPLE=posthog        # Analytics data (requires credentials)

# Legacy commands (still work)
make hackernews-example
make bitcoin-example
make posthog-example
```

### **Development Workflow**
1. Set up integration configuration
2. Run example script to validate setup
3. Review output for data quality
4. Integrate into main metric configurations

### **Production Validation**
- Run before deploying new integrations
- Verify credentials after rotation
- Test connectivity after infrastructure changes
- Validate data format consistency

## Best Practices for Example Scripts

### **Error Handling**
- Provide clear error messages for common issues
- Include troubleshooting guidance in error output
- Handle network timeouts and API rate limits
- Validate configuration before making API calls

### **Output Formatting**
- Display data in human-readable format
- Include metadata and context information
- Show data quality metrics and validation results
- Provide clear success/failure indicators

### **Configuration**
- Use environment variables for sensitive information
- Provide example .env files for setup
- Document all required configuration parameters
- Support both development and production configurations

### **Documentation**
- Include usage examples in script comments
- Document expected output and data formats
- Provide troubleshooting guidance
- Reference related configuration files

## Adding New Example Scripts

When creating new example scripts:

1. **Follow Naming Convention**: Use descriptive names like `{service}_example.py`
2. **Include Documentation**: Add comprehensive docstrings and comments
3. **Handle Errors Gracefully**: Provide helpful error messages and recovery guidance
4. **Test Thoroughly**: Validate with different configurations and edge cases
5. **Update README**: Document the new script and its purpose

### **Template Structure**
```python
#!/usr/bin/env python3
"""
Example script for {Service} integration testing.

This script validates {Service} credentials and tests data ingestion.
"""

from dotenv import load_dotenv
import pandas as pd
from your_integration import ingest_function

def main():
    """Main function with proper error handling."""
    try:
        load_dotenv(override=True)
        pd.set_option("display.max_columns", None)

        # Your integration logic here
        result = ingest_function()
        print(f"✅ Integration successful: {len(result)} records")
        print(result.head())

    except Exception as e:
        print(f"❌ Integration failed: {e}")
        print("Check your configuration and credentials")

if __name__ == "__main__":
    main()
```

## Integration with Testing

Example scripts can be integrated into automated testing workflows:

- **CI/CD Pipelines**: Validate integrations before deployment
- **Development Testing**: Quick validation during development
- **Production Monitoring**: Regular health checks of integrations
- **Documentation Testing**: Ensure examples stay current with codebase changes

## Troubleshooting Common Issues

### **API Authentication Errors**
- Verify API keys and credentials
- Check permission scopes and access levels
- Validate API endpoint URLs
- Review rate limiting and quota settings

### **Network Connectivity**
- Test network connectivity to external services
- Verify firewall and proxy configurations
- Check DNS resolution for service endpoints
- Validate SSL/TLS certificate handling

### **Data Format Issues**
- Review expected vs actual data formats
- Check data type conversions
- Validate timestamp formats and time zones
- Ensure proper encoding handling

### **Configuration Problems**
- Verify all required environment variables are set
- Check .env file loading and variable precedence
- Validate configuration file syntax
- Ensure proper service configuration in metrics/
