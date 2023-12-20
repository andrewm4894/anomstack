import json
import os
import pickle
from typing import List, Tuple

from dagster import get_dagster_logger
from google.cloud import storage
from google.oauth2 import service_account
from pyod.models.base import BaseDetector


def split_model_path(model_path) -> Tuple[str, str]:
    """
    Split model path into bucket and prefix.
    """

    model_path_parts = model_path.split("://")
    model_path_bucket = model_path_parts[1].split("/")[0]
    model_path_prefix = "/".join(model_path_parts[1].split("/")[1:])

    return model_path_bucket, model_path_prefix


def get_credentials():
    """
    Get credentials from environment variables.
    """

    credentials_path = os.getenv("ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS")
    credentials_json = os.getenv("ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS_JSON")

    if credentials_path:
        return service_account.Credentials.from_service_account_file(credentials_path)
    elif credentials_json:
        return service_account.Credentials.from_service_account_info(
            json.loads(credentials_json)
        )
    else:
        return None


def save_models_gcs(models, model_path, metric_batch) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models to gcs bucket.
    """

    logger = get_dagster_logger()

    model_path_bucket, model_path_prefix = split_model_path(model_path)

    credentials = get_credentials()
    storage_client = storage.Client(credentials=credentials)
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

    credentials = get_credentials()
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.get_bucket(model_path_bucket)

    model_name = f"{metric_name}.pkl"
    logger.info(f"loading {model_name} from {model_path}")

    blob = bucket.blob(f"{model_path_prefix}/{metric_batch}/{model_name}")

    with blob.open("rb") as f:
        model = pickle.load(f)

    return model
