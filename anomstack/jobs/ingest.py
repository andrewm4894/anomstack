"""
Generate ingest jobs and schedules.
"""

import pandas as pd
from dagster import (
    job, op, ScheduleDefinition, JobDefinition, DefaultScheduleStatus,
    get_dagster_logger
    )
from anomstack.config import specs
from anomstack.sql.render import render_sql
from anomstack.sql.read import read_sql
from anomstack.df.save import save_df


def build_ingest_job(spec) -> JobDefinition:
    """
    Build job definitions for ingest jobs.
    """

    metric_batch = spec['metric_batch']
    table_key = spec['table_key']
    gcp_project_id = spec['gcp_project_id']
    db = spec['db']


    @job(name=f'{metric_batch}_ingest')
    def _job():
        """
        Run SQL to calculate metrics and save to db.
        """

        @op(name=f'{metric_batch}_create_metrics')
        def create_metrics() -> pd.DataFrame:
            """
            Calculate metrics.
            """
            df = read_sql(render_sql('ingest_sql', spec), db)
            df["metric_batch"] = metric_batch
            df["metric_type"] = 'metric'
            return df

        @op(name=f'{metric_batch}_save_metrics')
        def save_metrics(df) -> pd.DataFrame:
            """
            Save metrics to db.
            """
            df = save_df(df, db, table_key, gcp_project_id)
            return df

        save_metrics(create_metrics())

    return _job


logger = get_dagster_logger()

# Build ingest jobs and schedules.
ingest_jobs = []
ingest_schedules = []
for spec in specs:
    logger.info(f'Building ingest job for {spec}')
    logger.info(f'Specs: \n{specs[spec]}')
    ingest_job = build_ingest_job(specs[spec])
    ingest_jobs.append(ingest_job)
    if specs[spec].get('ingest_default_schedule_status','STOPPED') == 'RUNNING':
        ingest_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        ingest_default_schedule_status = DefaultScheduleStatus.STOPPED
    ingest_schedule = ScheduleDefinition(
            job=ingest_job,
            cron_schedule=specs[spec]['ingest_cron_schedule'],
            default_status=ingest_default_schedule_status,
    )
    ingest_schedules.append(ingest_schedule)
