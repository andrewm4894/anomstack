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
        "cron_schedule": "*/2 * * * *",
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
    """Builds a job definition for a given ingest spec."""
    
    @job(name=spec["name"])
    def _job():
        """Job definition for a given ingest spec."""
        
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
jobs = [
    build_ingest_job(ingest_specs[ingest_spec]) 
    for ingest_spec in ingest_specs 
]

# define schedules
schedules = [
    ScheduleDefinition(
        job=job,
        cron_schedule=ingest_specs[job.name]['cron_schedule'],
    )
    for job in jobs
]

# create defs
defs = Definitions(
    jobs=jobs,
    schedules=schedules,
)
