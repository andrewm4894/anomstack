# DataFrame Utilities

This directory contains utilities for dataframe manipulation and processing within Anomstack's data pipeline.

## Overview

The `df` module provides essential dataframe operations for preparing, transforming, and managing metric data throughout the anomaly detection workflow.

## Components

### `wrangle.py`
- **Purpose**: Core data wrangling and transformation functions
- **Functions**:
  - Data cleaning and preprocessing
  - Column renaming and standardization
  - Data type conversions
  - Missing value handling
  - Feature engineering transformations

### `save.py`
- **Purpose**: DataFrame persistence and storage operations
- **Functions**:
  - Save processed dataframes to various formats
  - Batch writing operations
  - Data serialization for caching
  - Integration with external storage systems

### `utils.py`
- **Purpose**: Common dataframe utility functions
- **Functions**:
  - Data validation helpers
  - Common transformation patterns
  - DataFrame inspection utilities
  - Helper functions for data analysis

### `resample.py`
- **Purpose**: Time series resampling and aggregation
- **Functions**:
  - Temporal aggregation (hourly, daily, weekly)
  - Downsampling for different analysis frequencies
  - Gap filling and interpolation
  - Time-based grouping operations

## Data Flow

The typical data processing flow uses these utilities in sequence:

1. **Raw Data Ingestion** → Load from external sources
2. **Wrangling** → Clean and standardize using `wrangle.py`
3. **Resampling** → Aggregate to target frequency using `resample.py`
4. **Validation** → Check data quality using `utils.py`
5. **Persistence** → Save processed data using `save.py`

## Common Operations

### Data Cleaning
```python
from anomstack.df.wrangle import clean_metric_data

# Clean and standardize metric dataframe
df_clean = clean_metric_data(
    df_raw,
    timestamp_col='ts',
    value_col='metric_value'
)
```

### Time Series Resampling
```python
from anomstack.df.resample import resample_metrics

# Aggregate to hourly frequency
df_hourly = resample_metrics(
    df_clean,
    freq='1H',
    agg_method='mean'
)
```

### Data Validation
```python
from anomstack.df.utils import validate_metric_data

# Validate dataframe structure and content
is_valid = validate_metric_data(df_processed)
```

## Data Requirements

Dataframes processed by these utilities should typically have:

- **Timestamp Column**: DateTime index or column
- **Metric Value**: Numeric column with the metric values
- **Consistent Schema**: Standardized column names and data types
- **Proper Sorting**: Ordered by timestamp for time series operations

## Integration with Anomstack

These utilities are used throughout the Anomstack pipeline:

- **Ingestion Jobs**: Clean and standardize incoming data
- **Training Pipeline**: Prepare data for ML model training  
- **Scoring Pipeline**: Process new data points for anomaly detection
- **Dashboard**: Format data for visualization

## Performance Considerations

- **Memory Usage**: Large dataframes are processed in chunks when possible
- **Vectorization**: Operations use pandas vectorized functions for speed
- **Caching**: Intermediate results can be cached to avoid recomputation
- **Parallel Processing**: Some operations support parallel execution
