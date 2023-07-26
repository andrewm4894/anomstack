import os
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
)

from jobs.config import specs


def build_ingest_job(spec) -> JobDefinition:
    
    @job(name=f"{spec['name']}_ingest")
    def _job():
        
        logger = get_dagster_logger()
        
        @op(name=f"{spec['name']}_create_metrics")
        def create_metrics() -> pd.DataFrame:
            """Creates metrics."""
            df = pd.read_gbq(query=spec['ingest']['sql'])
            logger.info(f"df:\n{df}")
            return df
        
        @op(name=f"{spec['name']}_save_metrics")
        def save_metrics(df) -> pd.DataFrame:
            """Saves metrics."""
            df.to_gbq(
                destination_table=f"{spec['dataset']}.{spec['table']}",
                project_id=spec['project_id'],
                if_exists='append'
            )
            return df
        
        save_metrics(create_metrics())

    return _job


# generate jobs
ingest_jobs = [
    build_ingest_job(specs[spec]) 
    for spec in specs 
]

# define schedules
ingest_schedules = [
    ScheduleDefinition(
        job=ingest_job,
        cron_schedule=specs[ingest_job.name.replace('_ingest','')]['ingest']['cron_schedule'],
    )
    for ingest_job in ingest_jobs
]
