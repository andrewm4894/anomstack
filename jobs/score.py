import os
import pandas as pd
import pickle
from google.cloud import storage
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from jobs.config import specs
from jobs.utils import render_sql, read_sql


def build_score_job(spec) -> JobDefinition:
    
    @job(name=f"{spec['metric_batch']}_score")
    def _job():
        
        logger = get_dagster_logger()
        
        metric_batch = spec['metric_batch']
        bucket_name = spec['bucket_name']

        @op(name=f'{metric_batch}_get_score_data')
        def get_score_data() -> pd.DataFrame:
            df = read_sql(render_sql('score_sql', spec))
            return df

        @op(name=f'{metric_batch}_score_op')
        def score(df) -> pd.DataFrame:
            
            df_scores = pd.DataFrame()
            
            for metric_name in df['metric_name'].unique():
                
                df_metric = df[df['metric_name'] == metric_name].head(1)
                
                model_name = f'{metric_name}.pkl'
                logger.info(f'loading {model_name} from GCS bucket {bucket_name}')
                storage_client = storage.Client()
                bucket = storage_client.get_bucket(bucket_name)
                blob = bucket.blob(f'models/{model_name}')
                
                with blob.open('rb') as f:
                    model = pickle.load(f)
                    logger.info(model)
                    logger.info(df_metric)
                    scores = model.predict_proba(df_metric[['metric_value']])
                    df_score = pd.DataFrame({
                        'metric_timestamp': df_metric['metric_timestamp'].max(),
                        'metric_name': metric_name,
                        'anomaly_score': scores[0],
                    })
                    df_scores = pd.concat([df, pd.DataFrame([df_score])], ignore_index=True)
            
            logger.info(df_scores)

            return df

        score(get_score_data())

    return _job


# generate jobs
score_jobs = [build_score_job(specs[spec]) for spec in specs]

# define schedules
score_schedules = [
    ScheduleDefinition(
        job=score_job,
        cron_schedule=specs[score_job.name.replace('_score', '')][
            'score_cron_schedule'
        ],
    )
    for score_job in score_jobs
]
