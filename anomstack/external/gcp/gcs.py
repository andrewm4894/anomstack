from google.cloud import storage
from typing import List, Tuple
from pyod.models.base import BaseDetector
from dagster import get_dagster_logger
import pickle
import os
from google.oauth2 import service_account


def split_model_path(model_path) -> Tuple[str, str]:
    """
    Split model path into bucket and prefix.
    """

    model_path_parts = model_path.split("://")
    model_path_bucket = model_path_parts[1].split("/")[0]
    model_path_prefix = "/".join(model_path_parts[1].split("/")[1:])

    return model_path_bucket, model_path_prefix


def get_storage_client():
    """
    Get GCS storage client with credentials.
    """
    creds_json = os.environ.get('ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS_JSON')
    creds_file = os.environ.get('ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS')

    if creds_file:
        storage_client = storage.Client.from_service_account_json(creds_file)
    elif creds_json:
        creds = service_account.Credentials.from_authorized_user_info(creds_json)
        storage_client = storage.Client(credentials=creds)
    else:
        storage_client = storage.Client()

    return storage_client


def save_models_gcs(models, model_path, metric_batch) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models to gcs bucket.
    """

    logger = get_dagster_logger()

    model_path_bucket, model_path_prefix = split_model_path(model_path)

    storage_client = get_storage_client()
    bucket = storage_client.get_bucket(model_path_bucket)

    for metric, model in models:

        model_name = f"{metric}.pkl"
        logger.info(f"saving {model_name} to {model_path}")
        blob = bucket.blob(f"{model_path_prefix}/{metric_batch}/{model_name}")

        with blob.open("wb") as f:
            pickle.dump(model, f)

    return models


def load_model_gcs(metric_name, model_path, metric_batch) -> BaseDetector:
    """
    Load model.
    """

    logger = get_dagster_logger()

    model_path_bucket, model_path_prefix = split_model_path(model_path)

    model_name = f'{metric_name}.pkl'
    logger.info(f'loading {model_name} from {model_path}')

    storage_client = get_storage_client()
    bucket = storage_client.get_bucket(model_path_bucket)
    blob = bucket.blob(f'{model_path_prefix}/{metric_batch}/{model_name}')

    with blob.open('rb') as f:

        model = pickle.load(f)

    return model
