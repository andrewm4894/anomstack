"""
Generate train jobs and schedules.
"""

import pandas as pd
from pyod.models.base import BaseDetector
from dagster import (
    get_dagster_logger,
    job,
    op,
    ScheduleDefinition,
    JobDefinition,
    DefaultScheduleStatus,
)
from typing import List, Tuple
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.io.save import save_models
from anomstack.ml.train import train_model
from anomstack.fn.run import define_fn


def build_train_job(spec) -> JobDefinition:
    """
    Build job definitions for train jobs.

    Args:
        spec (dict): A dictionary containing the specifications for the train job.

    Returns:
        JobDefinition: A job definition for the train job.
    """

    metric_batch = spec["metric_batch"]
    db = spec["db"]
    model_path = spec["model_path"]
    preprocess_params = spec["preprocess_params"]
    model_name = spec["model_config"]["model_name"]
    model_params = spec["model_config"]["model_params"]

    @job(name=f"{metric_batch}_train")
    def _job():
        """
        Get data for training and train models.

        Returns:
            List[Tuple[str, BaseDetector]]: A list of tuples containing the metric name and the trained model.
        """

        logger = get_dagster_logger()

        @op(name=f"{metric_batch}_get_train_data")
        def get_train_data() -> pd.DataFrame:
            """
            Get data for training.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for training.
            """

            df = read_sql(render("train_sql", spec), db)

            return df

        @op(name=f"{metric_batch}_train_models")
        def train(df) -> List[Tuple[str, BaseDetector]]:
            """
            Train models.

            Args:
                df (pd.DataFrame): A pandas DataFrame containing the data for training.

            Returns:
                List[Tuple[str, BaseDetector]]: A list of tuples containing the metric name and the trained model.
            """

            preprocess = define_fn(fn_name="preprocess", fn=render("preprocess_fn", spec))

            models = []

            if len(df) == 0:
                logger.info(f"no data for {metric_batch} train job.")
                return models
            else:
                for metric_name in df["metric_name"].unique():
                    df_metric = df[df["metric_name"] == metric_name]
                    X = preprocess(
                        df_metric,
                        mode="train",
                        **preprocess_params
                    )
                    if len(X) > 0:
                        logger.info(
                            f"training {metric_name} in {metric_batch} train job. len(X)={len(X)}"
                        )
                        model = train_model(X, metric_name, model_name, model_params)
                        models.append((metric_name, model))
                    else:
                        logger.info(
                            f"no data for {metric_name} in {metric_batch} train job."
                        )
                return models

        @op(name=f"{metric_batch}_save_model")
        def save(models) -> List[Tuple[str, BaseDetector]]:
            """
            Save trained models.

            Args:
                models (List[Tuple[str, BaseDetector]]): A list of tuples containing the metric name and the trained model.

            Returns:
                List[Tuple[str, BaseDetector]]: A list of tuples containing the metric name and the trained model.
            """

            models = save_models(models, model_path, metric_batch)

            return models

        save(train(get_train_data()))

    return _job


# Build train jobs and schedules.
train_jobs = []
train_schedules = []
for spec_name, spec in specs.items():
    train_job = build_train_job(spec)
    train_jobs.append(train_job)
    if spec["train_default_schedule_status"] == "RUNNING":
        train_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        train_default_schedule_status = DefaultScheduleStatus.STOPPED
    train_schedule = ScheduleDefinition(
        job=train_job,
        cron_schedule=spec["train_cron_schedule"],
        default_status=train_default_schedule_status,
    )
    train_schedules.append(train_schedule)
