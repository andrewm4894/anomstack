# Python Ingest Simple Example

This **Anomstack metric batch** demonstrates how to use custom Python functions for data ingestion instead of SQL queries. Perfect for cases where you need to process data with Python libraries, call APIs, or perform complex transformations that are difficult to express in SQL.

## Overview

This example shows how to:
- Use the `ingest_fn` parameter to define custom Python data ingestion
- Create metrics programmatically using pandas DataFrames
- Replace SQL queries with Python logic
- Handle data processing that requires Python libraries
- Structure custom ingest functions for Anomstack

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`ingest.py`](ingest.py) to generate metrics using Python
2. **Train Job**: PyOD models learn patterns from the Python-generated data
3. **Score Job**: Generate anomaly scores for the metrics
4. **Alert Job**: Send notifications when anomalies are detected

### Python vs SQL Ingestion
- **SQL Ingestion**: Uses `ingest_sql` parameter with database queries
- **Python Ingestion**: Uses `ingest_fn` parameter with custom Python functions
- **When to Use Python**: Complex data transformations, API calls, machine learning preprocessing, file processing

## Files

- **[`ingest.py`](ingest.py)**: Custom Python ingest function
- **[`python_ingest_simple.yaml`](python_ingest_simple.yaml)**: Anomstack configuration

## Configuration Details

The YAML file configures:
```yaml
metric_batch: 'python_ingest_simple'
ingest_fn: 'ingest.py'  # Points to Python file instead of SQL
# All other settings inherited from defaults
```

### Python Function Requirements
Your custom ingest function must:
- Be named `ingest()`
- Return a pandas DataFrame
- Include columns: `metric_timestamp`, `metric_name`, `metric_value`
- Handle any errors gracefully

## Setup & Usage

### Prerequisites
- Anomstack environment set up
- Python libraries: pandas, numpy (included in Anomstack by default)
- Any additional libraries your function requires

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/python/python_ingest_simple metrics/my_python_batch
   ```

2. **Customize the ingest function**: Edit `ingest.py` to suit your needs

3. **Install dependencies**: Add any required packages to your environment

4. **Enable in Dagster**: The jobs will appear in your Dagster UI

### Example Python Function Structure
```python
import pandas as pd
from datetime import datetime

def ingest():
    """
    Custom ingest function that returns a pandas DataFrame
    with the required columns for Anomstack.
    """
    # Your custom logic here
    data = []

    # Example: Generate some metrics
    for i in range(3):
        data.append({
            'metric_timestamp': datetime.now(),
            'metric_name': f'python_metric_{i}',
            'metric_value': some_calculation(i)
        })

    return pd.DataFrame(data)

def some_calculation(x):
    # Your business logic
    return x * 10 + random.random()
```

## Common Use Cases

### API Data Processing
```python
import requests
import pandas as pd

def ingest():
    response = requests.get('https://api.example.com/data')
    data = response.json()

    metrics = []
    for item in data:
        metrics.append({
            'metric_timestamp': datetime.now(),
            'metric_name': f"api_metric_{item['type']}",
            'metric_value': item['value']
        })

    return pd.DataFrame(metrics)
```

### File Processing
```python
import pandas as pd
import os

def ingest():
    # Process CSV files
    df = pd.read_csv('data/metrics.csv')

    # Transform to required format
    return df.rename(columns={
        'timestamp': 'metric_timestamp',
        'name': 'metric_name',
        'value': 'metric_value'
    })
```

### Complex Calculations
```python
import numpy as np
import pandas as pd

def ingest():
    # Complex statistical calculations
    data = fetch_raw_data()  # Your data source

    metrics = []
    metrics.append({
        'metric_timestamp': datetime.now(),
        'metric_name': 'moving_average',
        'metric_value': np.mean(data[-30:])  # 30-day moving average
    })

    metrics.append({
        'metric_timestamp': datetime.now(),
        'metric_name': 'volatility',
        'metric_value': np.std(data[-30:])  # 30-day volatility
    })

    return pd.DataFrame(metrics)
```

## Error Handling

Always include proper error handling:
```python
def ingest():
    try:
        # Your ingest logic
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error in ingest function: {e}")
        # Return empty DataFrame on error
        return pd.DataFrame(columns=['metric_timestamp', 'metric_name', 'metric_value'])
```

## Environment Variables

Access environment variables for configuration:
```python
import os

def ingest():
    api_key = os.getenv('MY_API_KEY')
    endpoint = os.getenv('MY_API_ENDPOINT', 'https://default-api.com')

    # Use in your function
    response = requests.get(endpoint, headers={'Authorization': f'Bearer {api_key}'})
```

## Integration with Anomstack Features

- **Dashboard**: View Python-generated metrics in the FastHTML dashboard
- **Alerts**: Get notifications when your custom metrics show anomalies
- **Change Detection**: Detect changes in your Python-processed data
- **Model Storage**: Trained models work the same regardless of data source
- **Preprocessing**: Combine with custom preprocessing functions for advanced pipelines

This example provides the foundation for building sophisticated data ingestion pipelines while leveraging Anomstack's powerful anomaly detection capabilities.
