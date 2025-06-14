# Input/Output Utilities

This directory contains core I/O utilities for loading and saving data, models, and other artifacts in Anomstack.

## Overview

The `io` module provides standardized interfaces for data persistence across different storage backends, ensuring consistent data handling throughout the Anomstack pipeline.

## Components

### `load.py`
- **Purpose**: Data and model loading operations
- **Functions**:
  - Load metric data from various sources
  - Deserialize trained ML models
  - Read configuration files and metadata
  - Handle different file formats (JSON, pickle, parquet, etc.)
  - Implement caching mechanisms for frequently accessed data

### `save.py`
- **Purpose**: Data and model persistence operations
- **Functions**:
  - Save processed metric data
  - Serialize and store trained ML models
  - Write configuration and metadata files
  - Handle atomic writes to prevent data corruption
  - Implement versioning for models and artifacts

## Supported Storage Backends

The I/O utilities work with multiple storage systems:

- **Local Filesystem**: Direct file system operations
- **Cloud Storage**: Integration with S3, GCS, etc.
- **Databases**: Direct database read/write operations
- **Memory Cache**: In-memory storage for temporary data

## Common Use Cases

### Model Persistence
```python
from anomstack.io.save import save_model
from anomstack.io.load import load_model

# Save a trained model
save_model(
    model=trained_model,
    model_path="models/my_metric/model_20231215.pkl",
    metadata={"version": "1.0", "training_date": "2023-12-15"}
)

# Load the model later
loaded_model = load_model("models/my_metric/model_20231215.pkl")
```

### Data Serialization
```python
from anomstack.io.save import save_dataframe
from anomstack.io.load import load_dataframe

# Save processed metric data
save_dataframe(
    df=processed_metrics,
    path="data/processed/metrics_2023_12.parquet",
    format="parquet"
)

# Load the data
df = load_dataframe("data/processed/metrics_2023_12.parquet")
```

## File Format Support

The I/O utilities support multiple file formats:

- **Parquet**: Efficient columnar storage for large datasets
- **Pickle**: Python object serialization (for models)
- **JSON**: Configuration files and metadata
- **CSV**: Human-readable data export/import
- **HDF5**: High-performance scientific data storage

## Storage Path Conventions

Anomstack uses consistent path conventions:

```
/storage_root/
├── models/
│   ├── {metric_batch_name}/
│   │   ├── {metric_name}/
│   │   │   ├── model_{timestamp}.pkl
│   │   │   └── metadata_{timestamp}.json
├── data/
│   ├── raw/
│   ├── processed/
│   └── cache/
└── config/
    ├── metric_batches/
    └── system/
```

## Error Handling

The I/O utilities implement robust error handling:

- **Retry Logic**: Automatic retries for transient failures
- **Data Validation**: Verify data integrity after operations
- **Atomic Operations**: Ensure data consistency during writes
- **Graceful Degradation**: Fallback mechanisms for failures

## Performance Optimization

- **Lazy Loading**: Load data only when needed
- **Compression**: Automatic compression for storage efficiency
- **Chunked Operations**: Handle large datasets in manageable chunks
- **Connection Pooling**: Reuse connections for repeated operations

## Configuration

I/O operations can be configured through environment variables:

```bash
# Storage backend configuration
ANOMSTACK_STORAGE_BACKEND=local  # or 's3', 'gcs'
ANOMSTACK_STORAGE_ROOT=/path/to/storage

# Performance tuning
ANOMSTACK_IO_CHUNK_SIZE=10000
ANOMSTACK_IO_COMPRESSION=true
ANOMSTACK_IO_CACHE_TTL=3600
```

## Integration Points

The I/O utilities are used throughout Anomstack:

- **Jobs Pipeline**: Load/save data between job stages
- **Model Training**: Persist trained models and metadata
- **Dashboard**: Load data for visualization
- **External Integrations**: Interface with cloud storage
- **Configuration**: Load metric batch configurations

## Best Practices

- **Use appropriate file formats**: Parquet for large datasets, JSON for config
- **Implement proper error handling**: Always check for I/O failures
- **Use atomic operations**: Prevent partial writes and data corruption
- **Monitor storage usage**: Track storage consumption and cleanup old files
- **Version your artifacts**: Use timestamps or version numbers in filenames 