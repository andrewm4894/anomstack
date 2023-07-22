import os
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, Definitions, ScheduleDefinition, JobDefinition
)


ingest_specs = {
    "m1": {
        "name": "m1", 
        "sql": """
        select
          current_timestamp() as timestamp,
          'metric_1' as name,
          rand() as value,
        """, 
        "dataset": "tmp", 
        "table": "metrics", 
        "project_id": os.getenv("GCP_PROJECT"),
        "cron_schedule": "*/2 * * * *",
    },   
    "m2": {
        "name": "m2", 
        "sql": """
        select
          current_timestamp() as timestamp,
          'metric_2' as name,
          rand() as value,
        """,
        "dataset": "tmp", 
        "table": "metrics", 
        "project_id": os.getenv("GCP_PROJECT"),
        "cron_schedule": "*/3 * * * *",
    },
}


def build_ingest_job(spec) -> JobDefinition:
    
    @job(name=f"{spec['name']}_ingest")
    def _job():
        
        logger = get_dagster_logger()
        
        @op(name=f"{spec['name']}_create_metrics")
        def create_metrics() -> pd.DataFrame:
            """Creates metrics."""
            df = pd.read_gbq(query=spec['sql'])
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
    build_ingest_job(ingest_specs[ingest_spec]) 
    for ingest_spec in ingest_specs 
]

# define schedules
ingest_schedules = [
    ScheduleDefinition(
        job=ingest_job,
        cron_schedule=ingest_specs[ingest_job.name.replace('_ingest','')]['cron_schedule'],
    )
    for ingest_job in ingest_jobs
]
