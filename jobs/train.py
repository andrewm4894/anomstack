import os
import time
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, asset, Definitions, ScheduleDefinition, JobDefinition
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


def build_train_job(spec) -> JobDefinition:
    """Builds a job definition for a given train spec."""
    
    @job(name=f"{spec['name']}_train")
    def _job():
        """Job definition for a given train spec."""
        
        logger = get_dagster_logger()
        
        @op(name=f"{spec['name']}_get_train_data")
        def get_train_data() -> pd.DataFrame:
            """"""
            df = pd.read_gbq(query=spec['sql'])
            logger.info(f"df:\n{df}")
            return df
        
        @asset(
            name=f"{spec['name']}_train_model",
            io_manager_key="fs_io_manager",
        )
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

    return _job


# generate jobs
train_jobs = [
    build_train_job(train_specs[train_spec]) 
    for train_spec in train_specs 
]

# define schedules
train_schedules = [
    ScheduleDefinition(
        job=train_job,
        cron_schedule=train_specs[train_job.name.replace('_train','')]['cron_schedule'],
    )
    for train_job in train_jobs
]
