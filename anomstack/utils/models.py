from typing import List, Tuple
from pyod.models.base import BaseDetector
from anomstack.utils.gcs import save_models_gcs, load_model_gcs


def _save_models(models, model_path) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models.
    """
    
    if model_path.startswith('gs://'):
        models = save_models_gcs(models, model_path)
    else:
        raise ValueError(f"model_path {model_path} not supported")

    return models


def _load_model(metric_name, model_path) -> BaseDetector:
    """
    Load model.
    """
    
    if model_path.startswith('gs://'):
        model = load_model_gcs(metric_name, model_path)
    else:
        raise ValueError(f"model_path {model_path} not supported")
        
    return model