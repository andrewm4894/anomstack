# Google Cloud Platform Integration

This directory contains integrations for Google Cloud Platform services used by Anomstack.

## Services Supported

### BigQuery (`bigquery.py`)
- **Purpose**: Query metrics data from BigQuery tables
- **Features**:
  - Execute SQL queries against BigQuery datasets
  - Handle authentication and connection management
  - Support for parameterized queries
  - Automatic data type handling and conversion

### Google Cloud Storage (`gcs.py`)
- **Purpose**: Store and retrieve trained ML models
- **Features**:
  - Upload/download trained anomaly detection models
  - Model versioning and metadata management
  - Secure access with service account authentication
  - Bucket management and organization

### Authentication (`credentials.py`)
- **Purpose**: Manage GCP authentication and credentials
- **Features**:
  - Service account key management
  - Authentication token handling
  - Cross-service credential sharing
  - Secure credential storage

## Setup Requirements

### 1. Google Cloud Project
- Create a GCP project with billing enabled
- Enable required APIs:
  - BigQuery API
  - Cloud Storage API

### 2. Service Account
Create a service account with appropriate permissions:

```bash
# Create service account
gcloud iam service-accounts create anomstack-service \
    --display-name="Anomstack Service Account"

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:anomstack-service@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:anomstack-service@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

# Grant Storage permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:anomstack-service@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create anomstack-key.json \
    --iam-account=anomstack-service@PROJECT_ID.iam.gserviceaccount.com
```

### 3. Configuration

Set environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/anomstack-key.json"
export GCP_PROJECT_ID="your-project-id"
export GCS_BUCKET_NAME="your-anomstack-models-bucket"
```

## Usage Examples

### BigQuery Configuration
In your metric batch YAML file:

```yaml
data_source: bigquery
data_source_params:
  project_id: "your-project-id"
  dataset_id: "your_dataset"
  table_id: "your_metrics_table"
```

### GCS Configuration
For model storage:

```yaml
model_store: gcs
model_store_params:
  bucket_name: "your-anomstack-models-bucket"
  prefix: "models/"
```

## SQL Query Requirements

When using BigQuery, your SQL queries should:

1. Return at least two columns: timestamp and metric value
2. Use standard SQL (not legacy SQL)
3. Include proper date/time filtering for incremental loads
4. Handle null values appropriately

Example query structure:
```sql
SELECT
    timestamp_col as ds,
    metric_value as y
FROM `project.dataset.table`
WHERE timestamp_col >= @start_date
  AND timestamp_col < @end_date
ORDER BY timestamp_col
```

## Troubleshooting

### Common Issues

1. **Authentication errors**: Verify service account permissions and key file path
2. **BigQuery quota exceeded**: Check query complexity and dataset size
3. **GCS permissions**: Ensure bucket exists and service account has access
4. **Network connectivity**: Verify firewall rules and internet access

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger('google.cloud').setLevel(logging.DEBUG)
```
