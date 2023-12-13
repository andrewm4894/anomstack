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
from anomstack.config import specs
from anomstack.df.save import save_df
from anomstack.df.wrangle import wrangle_df
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.validate.validate import validate_df
from pyod.models.mad import MAD

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_change_job(spec) -> JobDefinition:
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

    @job(
        name=f"{metric_batch}_change",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Get data for change detection.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the data for change detection.
        """

        @op(name=f"{metric_batch}_get_change_data")
        def get_change_data() -> pd.DataFrame:
            """
            Get data for change detection.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for change detection.
            """
            df_change = read_sql(render("change_sql", spec), db)
            return df_change

        @op(name=f"{metric_batch}_detect_changes")
        def detect_changes(df_change) -> pd.DataFrame:
            """
            Run change detection.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for change detection.
            """
            logger.info(f"running change detection on {len(df_change)} rows")
            df_change_alerts = pd.DataFrame()
            # for each metric name
            for metric_name in df_change["metric_name"].unique():
                df_metric = df_change.query(f"metric_name=='{metric_name}'")
                df_metric["metric_alert"] = 0
                detector = MAD()
                # get the data for that metric excluding last observation
                X_train = df_metric["metric_value"].values[:-1]
                # ensure X_train is a 2D array
                X_train = X_train.reshape(-1, 1)
                X_new = df_metric["metric_value"].values[-1:]
                # ensure X_new is a 2D array
                X_new = X_new.reshape(-1, 1)
                X_new_timestamp = df_metric["metric_timestamp"].values[-1]
                detector.fit(X_train)
                X_train_scores = detector.decision_scores_
                # predict on the new data
                y_pred = detector.predict(X_new)
                y_pred_score = detector.decision_function(X_new)
                # append X_train_scores and y_pred_score to be a metric_score column
                metric_scores = list(X_train_scores) + list(y_pred_score)
                df_metric["metric_score"] = metric_scores
                logger.debug(f"df_metric:\n{df_metric}")
                # if the prediction is 1, then set metric_alert = 1 at the metric_timestamp of the new data
                if y_pred[0] == 1:
                    logger.info(
                        f"change detected for {metric_name} at {X_new_timestamp}"
                    )
                    df_metric.loc[
                        (df_metric["metric_timestamp"] == X_new_timestamp),
                        "metric_alert",
                    ] = 1
                    # append df_metric to df_change_alerts using concat
                    df_change_alerts = pd.concat([df_change_alerts, df_metric])
                else:
                    logger.info(
                        f"no change detected for {metric_name} at {X_new_timestamp}"
                    )
            return df_change_alerts

        @op(name=f"{metric_batch}_change_alerts_op")
        def alert(df_change_alerts) -> pd.DataFrame:
            """
            Alert on data.

            Args:
                df_change_alerts (pd.DataFrame): A pandas DataFrame containing the data for alerting.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for alerting.
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
                        f"🔥 [{metric_name}] looks changed ({metric_timestamp_max}) 🔥"
                    )
                    tags = {
                        "metric_batch": metric_batch,
                        "metric_name": metric_name,
                        "metric_timestamp": metric_timestamp_max,
                        "alert_type": "ml",
                        **metric_tags[metric_name],
                    }
                    logger.debug(f"metric tags:\n{tags}")
                    df_alert = send_alert(
                        metric_name=metric_name,
                        title=alert_title,
                        df=df_alert,
                        threshold=0,
                        alert_methods=alert_methods,
                        tags=tags,
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