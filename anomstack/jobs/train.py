"""
Generate train jobs and schedules.
"""

import pandas as pd
from pyod.models.base import BaseDetector
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from typing import List, Tuple
from anomstack.config import specs
from anomstack.utils.sql import render_sql, read_sql
from anomstack.utils.models import save_models
from anomstack.utils.ml import train_model, make_x


def build_train_job(spec) -> JobDefinition:
    """
    Build job definitions for train jobs.
    """
    
    metric_batch = spec['metric_batch']
    db = spec['db']
    model_path = spec['model_path']

    @job(name=f'{metric_batch}_train')
    def _job():
        """
        Get data for training and train models.
        """

        @op(name=f'{metric_batch}_get_train_data')
        def get_train_data() -> pd.DataFrame:
            """
            Get data for training.
            """
            
            df = read_sql(render_sql('train_sql', spec), db)
            
            return df

        @op(name=f'{metric_batch}_train_models')
        def train(df) -> List[Tuple[str, BaseDetector]]:
            """
            Train models.
            """
            
            models = []
            
            for metric_name in df["metric_name"].unique():
                
                df_metric = df[df['metric_name'] == metric_name]
                
                X = make_x(df_metric, mode='train')
                
                model = train_model(X, metric_name)
                
                models.append((metric_name, model))

            return models

        @op(name=f'{metric_batch}_save_model')
        def save(models) -> List[Tuple[str, BaseDetector]]:
            """
            Save trained models.
            """
            
            models = save_models(models, model_path)

            return models
        
        save(train(get_train_data()))

    return _job


train_jobs = [build_train_job(specs[spec]) for spec in specs]

train_schedules = [
    ScheduleDefinition(
        job=train_job,
        cron_schedule=specs[train_job.name.replace("_train", "")][
            "train_cron_schedule"
        ],
    )
    for train_job in train_jobs
]
