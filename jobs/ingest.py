import os
import pandas as pd
import jinja2
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from jobs.config import specs


def build_ingest_job(spec) -> JobDefinition:
    environment = jinja2.Environment()

    @job(name=f"{spec['batch']}_ingest")
    def _job():
        logger = get_dagster_logger()

        @op(name=f"{spec['batch']}_create_metrics")
        def create_metrics() -> pd.DataFrame:
            sql = environment.from_string(spec["ingest_sql"])
            sql = sql.render(
                table_key=spec["table_key"],
            )
            logger.info(f"sql:\n{sql}")
            df = pd.read_gbq(query=sql)
            df["batch"] = spec["batch"]
            logger.info(f"df:\n{df}")
            return df

        @op(name=f"{spec['batch']}_save_metrics")
        def save_metrics(df) -> pd.DataFrame:
            df.to_gbq(
                destination_table=f"{spec['table_key']}",
                project_id=spec["project_id"],
                if_exists="append",
            )
            return df

        save_metrics(create_metrics())

    return _job


# generate jobs
ingest_jobs = [build_ingest_job(specs[spec]) for spec in specs]

# define schedules
ingest_schedules = [
    ScheduleDefinition(
        job=ingest_job,
        cron_schedule=specs[ingest_job.name.replace("_ingest", "")][
            "ingest_cron_schedule"
        ],
    )
    for ingest_job in ingest_jobs
]