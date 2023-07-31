import pandas as pd
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from jobs.config import specs
from jobs.utils import read_sql, render_sql


def build_ingest_job(spec) -> JobDefinition:
    
    metric_batch = spec['metric_batch']
    table_key = spec['table_key']
    project_id = spec['project_id']
    if_exists = spec.get('if_exists','append')

    @job(name=f'{metric_batch}_ingest')
    def _job():

        @op(name=f'{metric_batch}_create_metrics')
        def create_metrics() -> pd.DataFrame:
            df = read_sql(render_sql('ingest_sql', spec))
            df["metric_batch"] = metric_batch
            return df

        @op(name=f'{metric_batch}_save_metrics')
        def save_metrics(df) -> pd.DataFrame:
            df.to_gbq(
                destination_table=table_key,
                project_id=project_id,
                if_exists=if_exists,
            )
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
