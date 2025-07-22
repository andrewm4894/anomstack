# Machine Learning Components

This directory contains the core machine learning functionality for Anomstack's anomaly detection system.

## Overview

Anomstack uses [PyOD (Python Outlier Detection)](https://pyod.readthedocs.io/en/latest/) for anomaly detection, providing multiple unsupervised ML algorithms to detect anomalies in your metrics.

## Components

### `preprocess.py`
- **Purpose**: Data preprocessing pipeline for metrics before ML training/scoring
- **Functions**:
  - Data cleaning and normalization
  - Feature engineering (lags, rolling statistics, etc.)
  - Handling missing values
  - Data transformation for ML algorithms

### `train.py`
- **Purpose**: Model training pipeline
- **Functions**:
  - Trains anomaly detection models on historical metric data
  - Supports multiple PyOD algorithms (Isolation Forest, OCSVM, etc.)
  - Model persistence and versioning
  - Hyperparameter optimization

### `change.py`
- **Purpose**: Change point detection and analysis
- **Functions**:
  - Detects significant changes in metric behavior
  - Identifies trend shifts and level changes
  - Provides context for anomaly alerts

## Anomaly Detection Process

1. **Data Ingestion**: Metrics are ingested from your data source
2. **Preprocessing**: Data is cleaned and features are engineered
3. **Training**: Models are trained on historical "normal" data
4. **Scoring**: New data points are scored against trained models
5. **Alert Generation**: Anomalies trigger alerts based on configured thresholds

## Supported Algorithms

Anomstack leverages PyOD's extensive algorithm library:

- **Isolation Forest**: Tree-based anomaly detection
- **One-Class SVM**: Support vector machine for outlier detection  
- **Local Outlier Factor (LOF)**: Density-based outlier detection
- **Autoencoder**: Neural network-based reconstruction error
- **And many more...**

## Configuration

ML parameters can be configured in your metric batch YAML files:

```yaml
ml_algorithm: "IsolationForest"
ml_params:
  contamination: 0.1
  n_estimators: 100
```

## Custom Preprocessing

You can override the default preprocessing by creating custom preprocessing functions in your metric batch configuration. See the main documentation for examples of custom preprocessing pipelines.
