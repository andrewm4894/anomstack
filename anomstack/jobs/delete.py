"""
Generate metric deletion jobs and schedules.
"""

import os

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
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv(
    "ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600
)


def build_delete_job(spec: dict) -> JobDefinition:
    """
    Build job definitions for delete jobs.

    Args:
        spec (dict): A dictionary containing the specifications for the delete job.

    Returns:
        JobDefinition: A job definition for the delete job.
    """

    if spec.get("disable_delete"):

        @job(
            name=f'{spec["metric_batch"]}_delete_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_delete_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    get_dagster_logger()

    metric_batch = spec["metric_batch"]
    db = spec["db"]
    spec["alert_methods"]
    spec["table_key"]
    spec.get("metric_tags", {})
    spec.get("delete_after_n_days", None)

    @job(
        name=f"{metric_batch}_delete",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Run delete job.
        """

        @op(name=f"{metric_batch}_delete_old_data")
        def delete_old_data() -> None:
            """
            Delete old data.

            Returns:
                None: None.
            """
            _ = read_sql(render("delete_sql", spec), db, returns_df=False)

            return None

        delete_old_data()

    return _job


# Build delete jobs and schedules.
delete_jobs = []
delete_schedules = []
specs = get_specs()
for spec_name, spec in specs.items():
    delete_job = build_delete_job(spec)
    delete_jobs.append(delete_job)
    if spec["delete_default_schedule_status"] == "RUNNING":
        delete_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        delete_default_schedule_status = DefaultScheduleStatus.STOPPED
    delete_schedule = ScheduleDefinition(
        job=delete_job,
        cron_schedule=spec["delete_cron_schedule"],
        default_status=delete_default_schedule_status,
    )
    delete_schedules.append(delete_schedule)
