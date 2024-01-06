"""
Functions for training models.
"""

import importlib
import time

from dagster import get_dagster_logger
from pyod.models.base import BaseDetector
import pandas as pd


def train_model(
    X: pd.DataFrame, metric: str, model_name: str, model_params: dict
) -> BaseDetector:
    """
    Train a model.

    Args:
        X (pd.DataFrame): The input data for training the model.
        metric (str): The metric used for training the model.
        model_name (str): The name of the model to be trained.
        model_params (dict): The parameters for the model.

    Returns:
        BaseDetector: The trained model.
    """

    logger = get_dagster_logger()

    model_class = getattr(
        importlib.import_module(f"pyod.models.{model_name.lower()}"), model_name
    )
    model = model_class(**model_params)

    time_start_train = time.time()
    model.fit(X)
    time_end_train = time.time()
    train_time = time_end_train - time_start_train
    logger.debug(
        f"trained model ({model_name}({model_params})) for {metric} (n={len(X)}, train_time={round(train_time,2)} secs)"
    )

    return model
