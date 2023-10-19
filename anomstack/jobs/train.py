"""
Generate train jobs and schedules.
"""

import pandas as pd
from pyod.models.base import BaseDetector
from dagster import (
    get_dagster_logger, job, op, ScheduleDefinition, JobDefinition,
    DefaultScheduleStatus
)
from typing import List, Tuple
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.io.save import save_models
from anomstack.ml.train import train_model
from anomstack.ml.preprocess import make_x


def build_train_job(spec) -> JobDefinition:
    """
    Build job definitions for train jobs.
    """

    metric_batch = spec['metric_batch']
    db = spec['db']
    model_path = spec['model_path']
    diff_n = spec['preprocess_diff_n']
    smooth_n = spec['preprocess_smooth_n']
    lags_n = spec['preprocess_lags_n']
    model_name = spec['model_config']['model_name']
    model_params = spec['model_config']['model_params']


    @job(name=f'{metric_batch}_train')
    def _job():
        """
        Get data for training and train models.
        """

        logger = get_dagster_logger()

        @op(name=f'{metric_batch}_get_train_data')
        def get_train_data() -> pd.DataFrame:
            """
            Get data for training.
            """

            df = read_sql(render('train_sql', spec), db)

            return df

        @op(name=f'{metric_batch}_train_models')
        def train(df) -> List[Tuple[str, BaseDetector]]:
            """
            Train models.
            """

            models = []

            for metric_name in df["metric_name"].unique():
                df_metric = df[df['metric_name'] == metric_name]
                X = make_x(df_metric, mode='train', diff_n=diff_n, smooth_n=smooth_n, lags_n=lags_n)
                if len(X) > 0:
                    logger.info(f'training {metric_name} in {metric_batch} train job. len(X)={len(X)}')
                    model = train_model(X, metric_name, model_name, model_params)
                    models.append((metric_name, model))
                else:
                    logger.info(f'no data for {metric_name} in {metric_batch} train job.')

            return models

        @op(name=f'{metric_batch}_save_model')
        def save(models) -> List[Tuple[str, BaseDetector]]:
            """
            Save trained models.
            """

            models = save_models(models, model_path, metric_batch)

            return models

        save(train(get_train_data()))

    return _job


# Build train jobs and schedules.
train_jobs = []
train_schedules = []
for spec in specs:
    train_job = build_train_job(specs[spec])
    train_jobs.append(train_job)
    if specs[spec]['train_default_schedule_status'] == 'RUNNING':
        train_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        train_default_schedule_status = DefaultScheduleStatus.STOPPED
    train_schedule = ScheduleDefinition(
            job=train_job,
            cron_schedule=specs[spec]['train_cron_schedule'],
            default_status=train_default_schedule_status,
    )
    train_schedules.append(train_schedule)
