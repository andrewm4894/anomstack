import os
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, Definitions, ScheduleDefinition, JobDefinition,
    AssetIn
)


score_specs = {
    "m1": {
        "name": "m1", 
        "sql": """
        select
          *
        from
          tmp.metrics
        where
          name = 'metric_1'
        order by timestamp desc
        limit 1
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
          *
        from
          tmp.metrics
        where
          name = 'metric_2'
        order by timestamp desc
        limit 1
        """,
        "dataset": "tmp", 
        "table": "metrics", 
        "project_id": os.getenv("GCP_PROJECT"),
        "cron_schedule": "*/3 * * * *",
    },
}


def build_score_job(spec) -> JobDefinition:
    
    @job(name=f"{spec['name']}_score")
    def _job():
        
        logger = get_dagster_logger()
        
        @op(name=f"{spec['name']}_get_score_data")
        def get_score_data() -> pd.DataFrame:
            df = pd.read_gbq(query=spec['sql'])
            logger.info(f"df:\n{df}")
            return df
        
        @op(
            name=f"{spec['name']}_score_op",
            #TODO: how to get model from upstream asset?
            #ins={"upstream_asset": AssetIn(key_prefix=f"{spec['name']}_model")}
        )
        def score(df) -> pd.DataFrame:
            #TODO: how to get model from upstream asset?
            logger.info(f"df:\n{df}")
            return df
        
        score(get_score_data())

    return _job


# generate jobs
score_jobs = [
    build_score_job(score_specs[score_spec]) 
    for score_spec in score_specs 
]

# define schedules
score_schedules = [
    ScheduleDefinition(
        job=score_job,
        cron_schedule=score_specs[score_job.name.replace('_score','')]['cron_schedule'],
    )
    for score_job in score_jobs
]
