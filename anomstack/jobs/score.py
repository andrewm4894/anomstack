"""
Generate score jobs and schedules.
"""

import pandas as pd
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from anomstack.config import specs
from anomstack.df.save import save_df
from anomstack.sql.render import render_sql
from anomstack.sql.read import read_sql
from anomstack.models_io.load import load_model
from anomstack.ml.preprocess import make_x


def build_score_job(spec) -> JobDefinition:
    """
    Build job definitions for score jobs.
    """
    
    logger = get_dagster_logger()
    
    metric_batch = spec['metric_batch']
    model_path = spec['model_path']
    table_key = spec['table_key']
    gcp_project_id = spec['gcp_project_id']
    db = spec['db']
    diff_n = spec['preprocess_diff_n']
    smooth_n = spec['preprocess_smooth_n']
    lags_n = spec['preprocess_lags_n']

    
    @job(name=f'{metric_batch}_score')
    def _job():
        """
        Get data for scoring and score data.
        """

        @op(name=f'{metric_batch}_get_score_data')
        def get_score_data() -> pd.DataFrame:
            """
            Get data for scoring.
            """
            
            df = read_sql(render_sql('score_sql', spec), db)
            
            return df

        @op(name=f'{metric_batch}_score_op')
        def score(df) -> pd.DataFrame:
            """
            Score data.
            """
            
            df_scores = pd.DataFrame()
            
            for metric_name in df['metric_name'].unique():
                
                df_metric = df[df['metric_name'] == metric_name]
                
                model = load_model(metric_name, model_path, metric_batch)
                
                X = make_x(df_metric, mode='score', diff_n=diff_n, smooth_n=smooth_n, lags_n=lags_n)
                
                scores = model.predict_proba(X)
                
                logger.debug(f"scores:\n{scores}")

                df_score = pd.DataFrame({
                    'metric_timestamp': df_metric['metric_timestamp'].max(),
                    'metric_name': metric_name,
                    'metric_value': [scores[0][1]], # probability of anomaly
                    'metric_batch': metric_batch,
                    'metric_type': 'score'
                })
                df_scores = pd.concat([df_scores, df_score], ignore_index=True)
            
            logger.debug(df_scores)

            return df_scores
        
        @op(name=f'{metric_batch}_save_scores')
        def save_scores(df) -> pd.DataFrame:
            """
            Save scores to db.
            """
            
            df = save_df(df, db, table_key, gcp_project_id)
            
            return df

        save_scores(score(get_score_data()))

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
