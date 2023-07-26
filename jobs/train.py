import os
import time
import pandas as pd
import pickle
from pyod.models.iforest import IForest
from pyod.models.base import BaseDetector
from dagster import (
    get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
)
from google.cloud import storage

from jobs.config import specs


def build_train_job(spec) -> JobDefinition:
    
    @job(name=f"{spec['name']}_train")
    def _job():
        
        logger = get_dagster_logger()
        
        @op(name=f"{spec['name']}_get_train_data")
        def get_train_data() -> pd.DataFrame:
            df = pd.read_gbq(query=spec['train']['sql'])
            logger.info(f"df:\n{df}")
            return df
        
        @op(name=f"{spec['name']}_train_model",)
        def train_model(df) -> BaseDetector:
            X = df[['value']].sample(frac=1).reset_index(drop=True)
            model = IForest()
            time_start_train = time.time()
            model.fit(X)
            time_end_train = time.time()
            train_time = time_end_train - time_start_train
            logger.info(f'trained model (n={len(X)}, train_time={round(train_time,2)} secs)')
            
            return model
        
        @op(name=f"{spec['name']}_save_model",)
        def save_model(model) -> BaseDetector:
            model_name = f"{spec['name']}.pkl"
            logger.info(f"saving {model_name} to GCS bucket {spec['bucket_name']}")
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(spec['bucket_name'])    
            blob = bucket.blob(f'models/{model_name}')
            with blob.open('wb') as f:
                pickle.dump(model, f)

            return model
        
        save_model(train_model(get_train_data()))

    return _job


# generate jobs
train_jobs = [
    build_train_job(specs[spec]) 
    for spec in specs 
]

# define schedules
train_schedules = [
    ScheduleDefinition(
        job=train_job,
        cron_schedule=specs[train_job.name.replace('_train','')]['train']['cron_schedule'],
    )
    for train_job in train_jobs
]
