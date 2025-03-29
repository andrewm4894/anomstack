"""
Generate ingest jobs and schedules.
"""

import os
from typing import Dict

import pandas as pd
from dagster import (
    MAX_RUNTIME_SECONDS_TAG,
    DefaultScheduleStatus,
    JobDefinition,
    ScheduleDefinition,
    get_dagster_logger,
    job,
    op,
)

from anomstack.config import get_specs
from anomstack.df.save import save_df
from anomstack.df.wrangle import wrangle_df
from anomstack.fn.run import run_df_fn
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.validate.validate import validate_df

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_ingest_job(spec: Dict) -> JobDefinition:
    """
    Build job definitions for ingest jobs.

    Args:
        spec (Dict): A dictionary containing the specifications for the job.

    Returns:
        JobDefinition: A job definition for the ingest job.
    """

    if spec.get("disable_ingest"):

        @job(
            name=f'{spec["metric_batch"]}_ingest_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    metric_batch = spec["metric_batch"]
    table_key = spec["table_key"]
    db = spec["db"]
    ingest_sql = spec.get("ingest_sql")
    ingest_fn = spec.get("ingest_fn")
    ingest_metric_rounding = spec.get("ingest_metric_rounding", 4)

    @job(
        name=f"{metric_batch}_ingest",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Run SQL to calculate metrics and save to db.
        """

        @op(name=f"{metric_batch}_create_metrics")
        def create_metrics() -> pd.DataFrame:
            """
            Calculate metrics.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the calculated metrics.
            """
            if ingest_sql:
                df = read_sql(render("ingest_sql", spec), db)
            elif ingest_fn:
                df = run_df_fn("ingest", render("ingest_fn", spec))
            else:
                raise ValueError(
                    f"No ingest_sql or ingest_fn specified for {metric_batch}."
                )
            logger.debug(f"df: \n{df}")
            df["metric_batch"] = metric_batch
            df["metric_type"] = "metric"
            df = wrangle_df(df, rounding=ingest_metric_rounding)
            df = validate_df(df)

            return df

        @op(name=f"{metric_batch}_save_metrics")
        def save_metrics(df: pd.DataFrame) -> pd.DataFrame:
            """
            Save metrics to db.

            Args:
                df (pd.DataFrame): A pandas DataFrame containing the metrics
                    to be saved.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the saved metrics.
            """
            df = save_df(df, db, table_key)

            return df

        save_metrics(create_metrics())

    return _job


logger = get_dagster_logger()

# Build ingest jobs and schedules.
ingest_jobs = []
ingest_schedules = []
specs = get_specs()
for spec_key, spec in specs.items():
    logger.debug(f"Building ingest job for {spec_key}")
    logger.debug(f"Specs: \n{spec}")
    ingest_job = build_ingest_job(spec)
    ingest_jobs.append(ingest_job)
    if spec.get("ingest_default_schedule_status", "STOPPED") == "RUNNING":
        ingest_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        ingest_default_schedule_status = DefaultScheduleStatus.STOPPED
    ingest_schedule = ScheduleDefinition(
        job=ingest_job,
        cron_schedule=spec["ingest_cron_schedule"],
        default_status=ingest_default_schedule_status,
    )
    ingest_schedules.append(ingest_schedule)
