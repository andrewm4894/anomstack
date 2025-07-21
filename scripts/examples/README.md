# Example Scripts

This directory contains example scripts and testing utilities to help you validate integrations, test functionality, and learn how to work with Anomstack.

## Scripts

### `posthog_example.py`
Example script for testing PostHog integration and validating credentials.

**Purpose:**
- Validates PostHog API credentials and configuration
- Tests the PostHog metrics ingestion pipeline
- Provides sample output to verify data collection
- Demonstrates proper PostHog integration setup

**Features:**
- Loads environment variables from .env file
- Executes PostHog ingest function
- Displays collected metrics in formatted output
- Error handling for common configuration issues

**Usage:**
```bash
cd scripts/examples/
python posthog_example.py
```

**Prerequisites:**
- PostHog credentials configured in environment variables
- `.env` file with PostHog configuration
- PostHog integration enabled in metrics configuration

**Environment Variables Required:**
- `POSTHOG_API_KEY` - Your PostHog API key
- `POSTHOG_PROJECT_ID` - Your PostHog project ID
- Other PostHog-specific configuration variables

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

### **Credential Validation**
```bash
# Test PostHog integration
python posthog_example.py

# Check for common issues
python posthog_example.py --debug
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