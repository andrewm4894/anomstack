from google.cloud import storage
from typing import List, Tuple
from pyod.models.base import BaseDetector
from dagster import get_dagster_logger
import pickle


def split_model_path(model_path) -> Tuple[str, str]:
    """
    Split model path into bucket and prefix.
    """
    
    model_path_parts = model_path.split("://")
    model_path_bucket = model_path_parts[1].split("/")[0]
    model_path_prefix = "/".join(model_path_parts[1].split("/")[1:])
    
    return model_path_bucket, model_path_prefix


def save_models_gcs(models, model_path) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models to gcs bucket.
    """
    
    logger = get_dagster_logger()
    
    model_path_bucket, model_path_prefix = split_model_path(model_path)
    
    for metric, model in models:
        
        model_name = f"{metric}.pkl"
        logger.info(f"saving {model_name} to {model_path}")
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(model_path_bucket)
        blob = bucket.blob(f"{model_path_prefix}/{model_name}")
        
        with blob.open("wb") as f:
            pickle.dump(model, f)

    return models


def load_model_gcs(metric_name, model_path) -> BaseDetector:
    """
    Load model.
    """
    
    logger = get_dagster_logger()
    
    model_path_bucket, model_path_prefix = split_model_path(model_path)
    
    model_name = f'{metric_name}.pkl'
    logger.info(f'loading {model_name} from {model_path}')
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(model_path_bucket)
    blob = bucket.blob(f'{model_path_prefix}/{model_name}')
    
    with blob.open('rb') as f:
        
        model = pickle.load(f)
        
    return model
