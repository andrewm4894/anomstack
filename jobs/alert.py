"""
Generate alert jobs and schedules.
"""

import pandas as pd
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from jobs.config import specs
from jobs.utils import render_sql, read_sql


def build_alert_job(spec) -> JobDefinition:
    """
    Build job definitions for alert jobs.
    """
    
    logger = get_dagster_logger()
    
    metric_batch = spec['metric_batch']
    
    @job(name=f'{metric_batch}_alerts')
    def _job():
        """
        Get data for alerting.
        """

        @op(name=f'{metric_batch}_get_alerts')
        def get_alerts() -> pd.DataFrame:
            """
            Get data for alerting.
            """
            df_alerts = read_sql(render_sql('alert_sql', spec))
            return df_alerts

        @op(name=f'{metric_batch}_alerts_op')
        def alert(df_alerts) -> pd.DataFrame:
            """
            Alert on data.
            """
            
            if len(df_alerts) == 0:
                logger.info('no alerts to send')
            else:
                logger.info(f'alerts to send: \n{df_alerts}')

            return df_alerts

        alert(get_alerts())

    return _job


# generate jobs
alert_jobs = [build_alert_job(specs[spec]) for spec in specs]

# define schedules
alert_schedules = [
    ScheduleDefinition(
        job=alert_job,
        cron_schedule=specs[alert_job.name.replace('_alerts', '')][
            'alert_cron_schedule'
        ],
    )
    for alert_job in alert_jobs
]
