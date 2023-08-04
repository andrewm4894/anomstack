import pandas as pd
import time
from pyod.models.base import BaseDetector
from pyod.models.iforest import IForest
from dagster import get_dagster_logger


def make_x(df, mode='train', diff_n=0, smooth_n=0, lags_n=0, score_n=1) -> pd.DataFrame:
    """
    Prepare data for model training and scoring.
    
    Parameters:
        diff_n (int): The order of differencing.
        smooth_n (int): The window size for smoothing (moving average).
        lags_n (list): The list of lags to include.
    """
    
    logger = get_dagster_logger()
    
    X = df.sort_values(by=['metric_timestamp']).reset_index(drop=True).set_index('metric_timestamp')
    X = df[["metric_value"]]
    
    if diff_n > 0:
        X['metric_value'] = X['metric_value'].diff(periods=diff_n).dropna()

    if smooth_n > 0:
        X['metric_value'] = X['metric_value'].rolling(window=smooth_n).mean().dropna()

    if lags_n > 0:
        for lag in range(1,lags_n+1):
            X[f'lag_{lag}'] = X['metric_value'].shift(lag)
    
    if mode == 'train':
        X = X.sample(frac=1)
        
    elif mode == 'score':
        X = X.tail(score_n)

    else:
        raise ValueError(f"mode must be 'train' or 'score'")

    X = X.dropna()
    
    logger.info(f'X=\n{X}')
    
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