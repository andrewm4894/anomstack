from typing import List, Tuple
from pyod.models.base import BaseDetector
from anomstack.gcp.gcs import load_model_gcs
import pickle


def load_model(metric_name, model_path, metric_batch) -> BaseDetector:
    """
    Load model.
    """
    
    if model_path.startswith('gs://'):
        model = load_model_gcs(metric_name, model_path, metric_batch)
    elif model_path.startswith('local://'):
        model = load_model_local(metric_name, model_path, metric_batch)
    else:
        raise ValueError(f"model_path {model_path} not supported")
        
    return model


def load_model_local(metric_name, model_path, metric_batch) -> BaseDetector:
    """
    Load model locally.
    """
    
    model_path = model_path.replace('local://', '')
    
    with open(f'{model_path}/{metric_batch}/{metric_name}.pkl', 'rb') as f:
        
        model = pickle.load(f)
    
    return model