"""
Generate change detection jobs and schedules.
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
from anomstack.config import get_specs
from anomstack.df.save import save_df
from anomstack.df.wrangle import wrangle_df
from anomstack.jinja.render import render
from anomstack.ml.change import detect_change
from anomstack.sql.read import read_sql
from anomstack.validate.validate import validate_df

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv(
    "ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600
)


def build_change_job(spec: dict) -> JobDefinition:
    """
    Build job definitions for change jobs.

    Args:
        spec (dict): A dictionary containing the specifications for the change job.

    Returns:
        JobDefinition: A job definition for the change job.
    """

    if spec.get("disable_change"):

        @job(
            name=f'{spec["metric_batch"]}_change_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_change_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    logger = get_dagster_logger()

    metric_batch = spec["metric_batch"]
    db = spec["db"]
    alert_methods = spec["alert_methods"]
    table_key = spec["table_key"]
    metric_tags = spec.get("metric_tags", {})
    change_threshold = spec.get("change_threshold", 3.5)
    change_detect_last_n = spec.get("change_detect_last_n", 1)

    @job(
        name=f"{metric_batch}_change",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Get data for change detection.
        """

        @op(name=f"{metric_batch}_get_change_data")
        def get_change_data() -> pd.DataFrame:
            """
            Get data for change detection.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for
                    change detection.
            """
            df_change = read_sql(render("change_sql", spec), db)

            return df_change

        @op(name=f"{metric_batch}_detect_changes")
        def detect_changes(df_change) -> pd.DataFrame:
            """
            Run change detection.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for
                    change detection.
            """
            logger.info(f"running change detection on {len(df_change)} rows")
            df_change_alerts = pd.DataFrame()
            for metric_name in df_change["metric_name"].unique():
                df_metric = df_change.query(
                    f"metric_name=='{metric_name}'"
                ).sort_values("metric_timestamp")
                df_metric = detect_change(
                    df_metric,
                    threshold=change_threshold,
                    detect_last_n=change_detect_last_n,
                )
                df_change_alerts = pd.concat([df_change_alerts, df_metric])

            return df_change_alerts

        @op(name=f"{metric_batch}_change_alerts_op")
        def alert(df_change_alerts) -> pd.DataFrame:
            """
            Alert on data.

            Args:
                df_change_alerts (pd.DataFrame): A pandas DataFrame containing
                    the data for alerting.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for
                    alerting.
            """

            if len(df_change_alerts) == 0:
                logger.info("no alerts to send")
            else:
                for metric_name in df_change_alerts["metric_name"].unique():
                    logger.info(f"alerting on {metric_name}")
                    df_alert = df_change_alerts.query(f"metric_name=='{metric_name}'")
                    df_alert["metric_timestamp"] = pd.to_datetime(
                        df_alert["metric_timestamp"]
                    )
                    metric_timestamp_max = (
                        df_alert["metric_timestamp"].max().strftime("%Y-%m-%d %H:%M")
                    )
                    alert_title = (
                        f"Δ [{metric_name}] looks changed ({metric_timestamp_max}) Δ"
                    )
                    tags = {
                        "metric_batch": metric_batch,
                        "metric_name": metric_name,
                        "metric_timestamp": metric_timestamp_max,
                        "alert_type": "change",
                        **metric_tags.get(metric_name, {}),
                    }
                    logger.debug(f"metric tags:\n{tags}")
                    df_alert = send_alert(
                        metric_name=metric_name,
                        title=alert_title,
                        df=df_alert,
                        threshold=change_threshold,
                        alert_methods=alert_methods,
                        tags=tags,
                        score_col="metric_score",
                        score_title="change_score",
                    )

            return df_change_alerts

        @op(name=f"{metric_batch}_save_change_alerts")
        def save_alerts(df_change_alerts: pd.DataFrame) -> pd.DataFrame:
            """
            Save alerts to db.

            Args:
                df (DataFrame): A pandas DataFrame containing the alerts to be saved.

            Returns:
                DataFrame: A pandas DataFrame containing the saved alerts.
            """

            if len(df_change_alerts) == 0:
                logger.info("no alerts to save")
                return df_change_alerts

            df_change_alerts = df_change_alerts.query("metric_alert == 1")

            if len(df_change_alerts) > 0:
                df_change_alerts["metric_type"] = "change"
                df_change_alerts["metric_alert"] = df_change_alerts[
                    "metric_alert"
                ].astype(float)
                df_change_alerts = df_change_alerts[
                    [
                        "metric_timestamp",
                        "metric_batch",
                        "metric_name",
                        "metric_type",
                        "metric_alert",
                    ]
                ]
                df_change_alerts = df_change_alerts.rename(
                    columns={"metric_alert": "metric_value"}
                )
                df_change_alerts = wrangle_df(df_change_alerts)
                df_change_alerts = validate_df(df_change_alerts)
                logger.info(
                    f"saving {len(df_change_alerts)} change alerts to {db} {table_key}"
                )
                df_change_alerts = save_df(df_change_alerts, db, table_key)
            else:
                logger.info("no alerts to save")

            return df_change_alerts

        save_alerts(alert(detect_changes(get_change_data())))

    return _job


# Build alert jobs and schedules.
change_jobs = []
change_schedules = []
specs = get_specs()
for spec_name, spec in specs.items():
    change_job = build_change_job(spec)
    change_jobs.append(change_job)
    if spec["change_default_schedule_status"] == "RUNNING":
        change_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        change_default_schedule_status = DefaultScheduleStatus.STOPPED
    change_schedule = ScheduleDefinition(
        job=change_job,
        cron_schedule=spec["change_cron_schedule"],
        default_status=change_default_schedule_status,
    )
    change_schedules.append(change_schedule)
