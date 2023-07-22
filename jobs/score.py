import os
import pandas as pd
import pickle
from google.cloud import storage
from dagster import (
    get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
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
        "bucket_name": os.getenv("GCS_BUCKET_NAME")
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
        "bucket_name": os.getenv("GCS_BUCKET_NAME")
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
        
        @op(name=f"{spec['name']}_score_op")
        def score(df) -> pd.DataFrame:
            model_name = f"{spec['name']}.pkl"
            logger.info(f"loading {model_name} from GCS bucket {spec['bucket_name']}")
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(spec['bucket_name'])    
            blob = bucket.blob(f'models/{model_name}')
            with blob.open('rb') as f:
                model = pickle.load(f)
            logger.info(model)
            logger.info(df)
            scores = model.predict_proba(df[['value']])
            logger.info(scores)
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
