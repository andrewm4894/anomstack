import pandas as pd
import time
from pyod.models.base import BaseDetector
from pyod.models.iforest import IForest
from dagster import get_dagster_logger


def make_x(df, mode='train') -> pd.DataFrame:
    """
    Prepare data for training.
    """
    
    if mode == 'train':
        X = (
            df[["metric_value"]]
            .sample(frac=1)
            .reset_index(drop=True)
        )
    elif mode == 'score':
        X = (
            df[["metric_value"]]
            .reset_index(drop=True)
        )
    else:
        raise ValueError(f"mode must be 'train' or 'score'")
    
    return X


def train_model(X, metric) -> BaseDetector:
    """
    Train a model.
    """
    
    logger = get_dagster_logger()
    
    model = IForest()
    time_start_train = time.time()
    model.fit(X)
    time_end_train = time.time()
    train_time = time_end_train - time_start_train
    logger.info(
        f"trained model for {metric} (n={len(X)}, train_time={round(train_time,2)} secs)"
    )
    
    return model