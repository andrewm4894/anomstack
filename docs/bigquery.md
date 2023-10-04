# BigQuery

Example of using BigQuery as a data source. See [`examples/bigquery`](/metrics/examples/bigquery/) directory for an example.

## Configuration

1. Set below environment variables in `.env` file.
    - `ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS`: Path to the Google Cloud Platform service account key file.  
    or
    - `ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS_JSON`: JSON string of the Google Cloud Platform service account key file.
    - `ANOMSTACK_GCP_PROJECT_ID`: Google Cloud Platform project ID.
    - `ANOMSTACK_MODEL_PATH`: Path to the model file on GCS (can also be set in metric batch config yaml as `model_path` param).
1. Configure metric batch config yaml file params.
    - `db: bigquery`: Set `db` param to `bigquery`.
