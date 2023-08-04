from typing import List, Tuple
from pyod.models.base import BaseDetector
from anomstack.utils.gcs import save_models_gcs, load_model_gcs
import pickle
import os


def save_models_local(models, model_path) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models locally.
    """
    
    model_path = model_path.replace('local://', '')
    
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    
    for metric_name, model in models:
        
        with open(f'{model_path}/{metric_name}.pkl', 'wb') as f:
            
            pickle.dump(model, f)
        
    return models


def save_models(models, model_path) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models.
    """
    
    if model_path.startswith('gs://'):
        models = save_models_gcs(models, model_path)
    elif model_path.startswith('local://'):
        models = save_models_local(models, model_path)
    else:
        raise ValueError(f"model_path {model_path} not supported")

    return models


def load_model(metric_name, model_path) -> BaseDetector:
    """
    Load model.
    """
    
    if model_path.startswith('gs://'):
        model = load_model_gcs(metric_name, model_path)
    elif model_path.startswith('local://'):
        model = load_model_local(metric_name, model_path)
    else:
        raise ValueError(f"model_path {model_path} not supported")
        
    return model


def load_model_local(metric_name, model_path) -> BaseDetector:
    """
    Load model locally.
    """
    
    model_path = model_path.replace('local://', '')
    
    with open(f'{model_path}/{metric_name}.pkl', 'rb') as f:
        
        model = pickle.load(f)
    
    return model