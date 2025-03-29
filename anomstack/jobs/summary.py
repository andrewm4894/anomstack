"""
Generate summary job and schedule.
"""

import os

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

from anomstack.alerts.send import send_df
from anomstack.config import get_specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_summary_job(spec: dict) -> JobDefinition:
    """
    Build job definitions for summary jobs.

    Args:
        spec (dict): A dictionary containing the specifications for the summary job.

    Returns:
        JobDefinition: A job definition for the summary job.
    """

    if spec.get("disable_summary"):

        @job(
            name=f'{spec["metric_batch"]}_summary_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    logger = get_dagster_logger()

    db = spec["db"]
    table_key = spec["table_key"]

    @job(
        name="summary",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Get data for summary.
        """

        @op(name="get_summary")
        def get_summary() -> pd.DataFrame:
            """
            Get data for summary.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for summary.
            """
            df_summary = read_sql(render("summary_sql", spec), db)

            return df_summary

        @op(name="send_summary")
        def send_summary(df_summary) -> pd.DataFrame:
            """ """

            logger.info(f"sending {len(df_summary)} summary to {db} {table_key}")
            send_df(
                title="Anomstack Summary",
                df=df_summary,
            )

            return df_summary

        send_summary(get_summary())

    return _job


# Build summary job and schedule.
specs = get_specs()
spec = specs[list(specs.keys())[0]]
spec["name"] = "summary"
summary_job = build_summary_job(spec)
summary_jobs = [summary_job]
summary_default_schedule_status = DefaultScheduleStatus.RUNNING
summary_schedule = ScheduleDefinition(
    job=summary_job,
    cron_schedule=spec["summary_cron_schedule"],
    default_status=summary_default_schedule_status,
)
summary_schedules = [summary_schedule]
