"""
Generate alert jobs and schedules.
"""

import os

import pandas as pd
from dagster import (
    MAX_RUNTIME_SECONDS_TAG,
    DefaultScheduleStatus,
    JobDefinition,
    ScheduleDefinition,
    get_dagster_logger,
    job,
    op,
)

from anomstack.alerts.send import send_alert
from anomstack.config import specs
from anomstack.df.save import save_df
from anomstack.df.wrangle import wrangle_df
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.validate.validate import validate_df

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_alert_job(spec: dict) -> JobDefinition:
    """
    Build job definitions for alert jobs.

    Args:
        spec (dict): A dictionary containing the specifications for the alert job.

    Returns:
        JobDefinition: A job definition for the alert job.
    """

    if spec.get("disable_alerts"):

        @job(
            name=f'{spec["metric_batch"]}_alerts_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    logger = get_dagster_logger()

    metric_batch = spec["metric_batch"]
    db = spec["db"]
    threshold = spec["alert_threshold"]
    alert_methods = spec["alert_methods"]
    table_key = spec["table_key"]
    metric_tags = spec.get("metric_tags", {})

    @job(
        name=f"{metric_batch}_alerts",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Get data for alerting.
        """

        @op(name=f"{metric_batch}_get_alerts")
        def get_alerts() -> pd.DataFrame:
            """
            Get data for alerting.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for alerting.
            """
            df_alerts = read_sql(render("alert_sql", spec), db)

            return df_alerts

        @op(name=f"{metric_batch}_alerts_op")
        def alert(df_alerts) -> pd.DataFrame:
            """
            Alert on data.

            Args:
                df_alerts (pd.DataFrame): A pandas DataFrame containing the
                    data for alerting.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for
                    alerting.
            """

            if len(df_alerts) == 0:
                logger.info("no alerts to send")
            else:
                for metric_name in df_alerts["metric_name"].unique():
                    logger.info(f"alerting on {metric_name}")
                    df_alert = df_alerts.query(f"metric_name=='{metric_name}'")
                    df_alert["metric_timestamp"] = pd.to_datetime(
                        df_alert["metric_timestamp"]
                    )
                    metric_timestamp_max = (
                        df_alert["metric_timestamp"].max().strftime("%Y-%m-%d %H:%M")
                    )
                    alert_title = (
                        f"🔥 [{metric_name}] looks anomalous ({metric_timestamp_max}) 🔥"
                    )
                    tags = {
                        "metric_batch": metric_batch,
                        "metric_name": metric_name,
                        "metric_timestamp": metric_timestamp_max,
                        "alert_type": "ml",
                        **metric_tags.get(metric_name, {}),
                    }
                    logger.debug(f"metric tags:\n{tags}")
                    df_alert = send_alert(
                        metric_name=metric_name,
                        title=alert_title,
                        df=df_alert,
                        threshold=threshold,
                        alert_methods=alert_methods,
                        tags=tags,
                    )

            return df_alerts

        @op(name=f"{metric_batch}_save_alerts")
        def save_alerts(df_alerts: pd.DataFrame) -> pd.DataFrame:
            """
            Save alerts to db.

            Args:
                df (DataFrame): A pandas DataFrame containing the alerts to be saved.

            Returns:
                DataFrame: A pandas DataFrame containing the saved alerts.
            """

            df_alerts = df_alerts.query("metric_alert == 1")

            if len(df_alerts) > 0:
                df_alerts["metric_type"] = "alert"
                df_alerts["metric_alert"] = df_alerts["metric_alert"].astype(float)
                df_alerts = df_alerts[
                    [
                        "metric_timestamp",
                        "metric_batch",
                        "metric_name",
                        "metric_type",
                        "metric_alert",
                    ]
                ]
                df_alerts = df_alerts.rename(columns={"metric_alert": "metric_value"})
                df_alerts = wrangle_df(df_alerts)
                df_alerts = validate_df(df_alerts)
                logger.info(f"saving {len(df_alerts)} alerts to {db} {table_key}")
                df_alerts = save_df(df_alerts, db, table_key)
            else:
                logger.info("no alerts to save")

            return df_alerts

        save_alerts(alert(get_alerts()))

    return _job


# Build alert jobs and schedules.
alert_jobs = []
alert_schedules = []
for spec_name, spec in specs.items():
    alert_job = build_alert_job(spec)
    alert_jobs.append(alert_job)
    if spec["alert_default_schedule_status"] == "RUNNING":
        alert_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        alert_default_schedule_status = DefaultScheduleStatus.STOPPED
    alert_schedule = ScheduleDefinition(
        job=alert_job,
        cron_schedule=spec["alert_cron_schedule"],
        default_status=alert_default_schedule_status,
    )
    alert_schedules.append(alert_schedule)
