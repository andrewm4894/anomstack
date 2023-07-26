import os
import pandas as pd
import pickle
from google.cloud import storage
from dagster import (
    get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
)

from jobs.config import specs


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
    build_score_job(specs[spec]['score']) 
    for spec in specs 
]

# define schedules
score_schedules = [
    ScheduleDefinition(
        job=score_job,
        cron_schedule=specs[score_job.name.replace('_score','')]['score']['cron_schedule'],
    )
    for score_job in score_jobs
]
