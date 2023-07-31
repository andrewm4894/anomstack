import os
import pandas as pd
import pickle
from google.cloud import storage
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
import jinja2
from jobs.config import specs


environment = jinja2.Environment()


def build_score_job(spec) -> JobDefinition:
    @job(name=f"{spec['metric_batch']}_score")
    def _job():
        logger = get_dagster_logger()

        @op(name=f"{spec['metric_batch']}_get_score_data")
        def get_score_data() -> pd.DataFrame:
            sql = environment.from_string(spec["score_sql"])
            sql = sql.render(
                table_key=spec["table_key"],
                metric_batch=spec["metric_batch"],
            )
            logger.info(f"sql:\n{sql}")
            df = pd.read_gbq(query=sql)
            logger.info(f"df:\n{df}")
            return df

        @op(name=f"{spec['metric_batch']}_score_op")
        def score(df) -> pd.DataFrame:
            for metric in df["metric_name"].unique():
                df_metric = df[df["metric_name"] == metric].head(1)
                model_name = f"{metric}.pkl"
                logger.info(
                    f"loading {model_name} from GCS bucket {spec['bucket_name']}"
                )
                storage_client = storage.Client()
                bucket = storage_client.get_bucket(spec["bucket_name"])
                blob = bucket.blob(f"models/{model_name}")
                with blob.open("rb") as f:
                    model = pickle.load(f)
                logger.info(model)
                logger.info(df_metric)
                scores = model.predict_proba(df_metric[["metric_value"]])
                logger.info(scores)

            return df

        score(get_score_data())

    return _job


# generate jobs
score_jobs = [build_score_job(specs[spec]) for spec in specs]

# define schedules
score_schedules = [
    ScheduleDefinition(
        job=score_job,
        cron_schedule=specs[score_job.name.replace("_score", "")][
            "score_cron_schedule"
        ],
    )
    for score_job in score_jobs
]
