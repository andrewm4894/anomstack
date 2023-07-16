import os
import pandas as pd
from dagster import (
    get_dagster_logger, job, op, Definitions, ScheduleDefinition, JobDefinition
)


train_specs = {
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
        limit 1000
        """,
        "cron_schedule": "*/4 * * * *",
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
        limit 1000
        """,
        "cron_schedule": "*/5 * * * *",
    },
}


def build_train_job(spec) -> JobDefinition:
    """Builds a job definition for a given train spec."""
    
    @job(name=f"{spec['name']}_train")
    def _job():
        """Job definition for a given train spec."""
        
        logger = get_dagster_logger()
        
        @op(name=f"{spec['name']}_get_train_data")
        def get_train_data() -> pd.DataFrame:
            """"""
            df = pd.read_gbq(query=spec['sql'])
            logger.info(f"df:\n{df}")
            return df
        
        @op(name=f"{spec['name']}_train_model")
        def train_model(df) -> pd.DataFrame:
            """"""
            logger.info(f"TODO: train model")
            return df
        
        train_model(get_train_data())

    return _job


# generate jobs
train_jobs = [
    build_train_job(train_specs[train_spec]) 
    for train_spec in train_specs 
]

# define schedules
train_schedules = [
    ScheduleDefinition(
        job=train_job,
        cron_schedule=train_specs[train_job.name.replace('_train','')]['cron_schedule'],
    )
    for train_job in train_jobs
]
