import os
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, Definitions, ScheduleDefinition, JobDefinition
)


ingest_specs = {
    "m1": {
        "name": "m1", 
        "sql": "select 111", 
        "dataset": "tmp", 
        "table": "test", 
        "project_id": os.getenv("GCP_PROJECT"),
        "cron_schedule": "*/3 * * * *",
    },   
    "m2": {
        "name": "m2", 
        "sql": "select 222", 
        "dataset": "tmp", 
        "table": "test", 
        "project_id": os.getenv("GCP_PROJECT"),
        "cron_schedule": "*/3 * * * *",
    },
}


def build_ingest_job(spec) -> JobDefinition:
    
    @job(name=spec["name"])
    def _job():
        
        logger = get_dagster_logger()
        
        @op(name=f"{spec['name']}_create_metrics")
        def create_metrics() -> pd.DataFrame:
            df = pd.read_gbq(query=spec['sql'])
            logger.info(f"df:\n{df}")
            return df
        
        @op(name=f"{spec['name']}_save_metrics")
        def save_metrics(df) -> pd.DataFrame:
            df.to_gbq(
                destination_table=f"{spec['dataset']}.{spec['table']}",
                project_id=spec['project_id'],
                if_exists='append'
            )
            return df
        
        save_metrics(create_metrics())

    return _job


jobs = [
    build_ingest_job(ingest_specs[ingest_spec]) 
    for ingest_spec in ingest_specs 
]

schedules = [
    ScheduleDefinition(
        job=job,
        cron_schedule=ingest_specs[job.name]['cron_schedule'],
    )
    for job in jobs
]

defs = Definitions(
    jobs=jobs,
    schedules=schedules,
)
