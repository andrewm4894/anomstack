"""
Some helper functions for loading models.
"""

import pickle
from pyod.models.base import BaseDetector
from anomstack.external.aws.s3 import load_model_s3
from anomstack.external.gcp.gcs import load_model_gcs


def load_model(metric_name: str, model_path: str, metric_batch: str) -> BaseDetector:
    """
    Load model.

    Args:
        metric_name (str): The name of the metric.
        model_path (str): The path to the model.
        metric_batch (str): The batch of the metric.

    Returns:
        BaseDetector: The loaded model.

    Raises:
        ValueError: If the model_path is not supported.
    """

    if model_path.startswith("gs://"):
        model = load_model_gcs(metric_name, model_path, metric_batch)
    elif model_path.startswith("s3://"):
        model = load_model_s3(metric_name, model_path, metric_batch)
    elif model_path.startswith("local://"):
        model = load_model_local(metric_name, model_path, metric_batch)
    else:
        raise ValueError(f"model_path {model_path} not supported")

    return model


def load_model_local(
    metric_name: str, model_path: str, metric_batch: str
) -> BaseDetector:
    """
    Load model locally.

    Args:
        metric_name (str): The name of the metric.
        model_path (str): The path to the model.
        metric_batch (str): The batch of the metric.

    Returns:
        BaseDetector: The loaded model.
    """

    model_path = model_path.replace("local://", "")

    with open(f"{model_path}/{metric_batch}/{metric_name}.pkl", "rb") as f:
        model = pickle.load(f)

    return model
