import os
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, Definitions, ScheduleDefinition, JobDefinition, schedule
)


specs = {
    'spec1':[
        {
            "name": "m1", 
            "sql": "select 111", 
            "dataset": "tmp", 
            "table": "test", 
            "project_id": os.getenv("GCP_PROJECT"),
            "cron_schedule": "*/3 * * * *",
        },   
    ],
    'spec2':[
        {
            "name": "m2", 
            "sql": "select 222", 
            "dataset": "tmp", 
            "table": "test", 
            "project_id": os.getenv("GCP_PROJECT"),
            "cron_schedule": "*/3 * * * *",
        },
    ],
}


def build_ingest_job(spec) -> JobDefinition:
    @job(
        name=spec["name"], 
    )
    def _job():
        
        logger = get_dagster_logger()
        
        @op(
            name=f"create_table_{spec['name']}",
        )
        def create_metrics() -> pd.DataFrame:
            df = pd.read_gbq(
                query=spec['sql'],
            )
            logger.info(f"df:\n{df}")
            return df
        
        @op(
            name=f"save_metrics_{spec['name']}",
        )
        def save_metrics(df) -> pd.DataFrame:
            df.to_gbq(
                destination_table=f"{spec['dataset']}.{spec['table']}",
                project_id=spec['project_id'],
                if_exists='append'
            )
            return df
        
        save_metrics(create_metrics())

    return _job


def build_ingest_schedule(spec):
    @schedule(
        name=f"schedule_{spec['name']}",
        cron_schedule=spec['cron_schedule'],
        job_name=spec['name'],
    )
    def _schedule():
        
        ScheduleDefinition(
            name=f"schedule_{spec['name']}",
            job=spec['name'],
            cron_schedule=spec['cron_schedule'],
        )
    
    return _schedule


jobs = [
    build_ingest_job(s) 
    for spec in specs 
    for s in specs[spec]
]

schedules = [
    build_ingest_schedule(s) 
    for spec in specs 
    for s in specs[spec]
]

defs = Definitions(
    jobs=jobs,
    schedules=schedules,
)
