"""
Generate ingest jobs and schedules.
"""

import pandas as pd
from dagster import job, op, ScheduleDefinition, JobDefinition
from anomstack.config import specs
from anomstack.utils.sql import read_sql, render_sql, save_df


def build_ingest_job(spec) -> JobDefinition:
    """
    Build job definitions for ingest jobs.
    """
    
    metric_batch = spec['metric_batch']
    table_key = spec['table_key']
    project_id = spec['project_id']
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
            df = save_df(df, db, table_key, project_id)
            return df

        save_metrics(create_metrics())

    return _job


# generate jobs
ingest_jobs = [build_ingest_job(specs[spec]) for spec in specs]

# define schedules
ingest_schedules = [
    ScheduleDefinition(
        job=ingest_job,
        cron_schedule=specs[ingest_job.name.replace('_ingest', '')][
            'ingest_cron_schedule'
        ],
    )
    for ingest_job in ingest_jobs
]
