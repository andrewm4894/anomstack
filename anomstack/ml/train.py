import time
import importlib
from pyod.models.base import BaseDetector
from dagster import get_dagster_logger


def train_model(X, metric, model_name, model_params) -> BaseDetector:
    """
    Train a model.
    """

    logger = get_dagster_logger()

    model_class = getattr(importlib.import_module(f'pyod.models.{model_name.lower()}'), model_name)
    model = model_class(**model_params)

    time_start_train = time.time()
    model.fit(X)
    time_end_train = time.time()
    train_time = time_end_train - time_start_train
    logger.info(
        f"trained model ({model_name}({model_params})) for {metric} (n={len(X)}, train_time={round(train_time,2)} secs)"
    )

    return model
