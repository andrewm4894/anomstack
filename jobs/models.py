import os
import time
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, asset, Definitions, ScheduleDefinition, JobDefinition,
    define_asset_job, FreshnessPolicy, AutoMaterializePolicy
)
from pyod.models.iforest import IForest
from pyod.models.base import BaseDetector


train_specs = {
    "m1": {
        "name": "m1", 
        "sql": """
        select
          *
        from
          tmp.metrics
        where
          name = 'metric_1'
        order by timestamp desc
        limit 1000
        """,
        "cron_schedule": "*/4 * * * *",
    },
    "m2": {
        "name": "m2", 
        "sql": """
        select
          *
        from
          tmp.metrics
        where
          name = 'metric_2'
        order by timestamp desc
        limit 1000
        """,
        "cron_schedule": "*/5 * * * *",
    },
}


def build_model_asset(spec) -> JobDefinition:
    """Builds a job definition for a given train spec."""
    
    @asset(
        group_name=f"{spec['name']}_model",
        name=f"{spec['name']}_model", 
        metadata={'metric': spec['name']},
        auto_materialize_policy=AutoMaterializePolicy.eager(),
        freshness_policy=FreshnessPolicy(maximum_lag_minutes=5)
    )
    def _model():
        """Job definition for a given train spec."""
        
        logger = get_dagster_logger()
        
        def get_train_data() -> pd.DataFrame:
            """"""
            df = pd.read_gbq(query=spec['sql'])
            logger.info(f"df:\n{df}")
            return df
        
        def train_model(df) -> BaseDetector:
            """"""
            X = df[['value']].sample(frac=1).reset_index(drop=True)
            model = IForest()
            time_start_train = time.time()
            model.fit(X)
            time_end_train = time.time()
            train_time = time_end_train - time_start_train
            logger.info(f'trained model (n={len(X)}, train_time={round(train_time,2)} secs)')
            
            return model
        
        train_model(get_train_data())

    return _model


# generate models
models = [
    build_model_asset(train_specs[train_spec]) 
    for train_spec in train_specs 
]
