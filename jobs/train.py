"""
Generate train jobs and schedules.
"""

import os
import time
import pandas as pd
import pickle
from pyod.models.iforest import IForest
from pyod.models.base import BaseDetector
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from google.cloud import storage
import jinja2
from typing import List, Tuple
from jobs.config import specs
from jobs.utils import render_sql, read_sql


def build_train_job(spec) -> JobDefinition:
    """
    Build job definitions for train jobs.
    """

    @job(name=f"{spec['metric_batch']}_train")
    def _job():
        """
        Get data for training and train models.
        """
        
        logger = get_dagster_logger()

        @op(name=f"{spec['metric_batch']}_get_train_data")
        def get_train_data() -> pd.DataFrame:
            """
            Get data for training.
            """
            
            df = read_sql(render_sql('train_sql', spec))
            
            return df

        @op(name=f"{spec['metric_batch']}_train_models")
        def train_models(df) -> List[Tuple[str, BaseDetector]]:
            """
            Train models.
            """
            
            models = []
            
            for metric in df["metric_name"].unique():
                
                X = (
                    df.query(f"metric_name=='{metric}'")[["metric_value"]]
                    .sample(frac=1)
                    .reset_index(drop=True)
                )
                model = IForest()
                time_start_train = time.time()
                model.fit(X)
                time_end_train = time.time()
                train_time = time_end_train - time_start_train
                logger.info(
                    f"trained model for {metric} (n={len(X)}, train_time={round(train_time,2)} secs)"
                )
                models.append((metric, model))

            return models

        @op(name=f"{spec['metric_batch']}_save_model")
        def save_models(models) -> List[Tuple[str, BaseDetector]]:
            """
            Save trained models to bucket.
            """
            
            for metric, model in models:
                
                model_name = f"{metric}.pkl"
                logger.info(f"saving {model_name} to GCS bucket {spec['bucket_name']}")
                storage_client = storage.Client()
                bucket = storage_client.get_bucket(spec["bucket_name"])
                blob = bucket.blob(f"models/{model_name}")
                
                with blob.open("wb") as f:
                    pickle.dump(model, f)

            return models
        
        save_models(train_models(get_train_data()))

    return _job


# generate jobs
train_jobs = [build_train_job(specs[spec]) for spec in specs]

# define schedules
train_schedules = [
    ScheduleDefinition(
        job=train_job,
        cron_schedule=specs[train_job.name.replace("_train", "")][
            "train_cron_schedule"
        ],
    )
    for train_job in train_jobs
]
