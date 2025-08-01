"""
Generate llmalert jobs and schedules.
"""

import json
import os

from dagster import (
    MAX_RUNTIME_SECONDS_TAG,
    DefaultScheduleStatus,
    JobDefinition,
    ScheduleDefinition,
    get_dagster_logger,
    job,
    op,
)
import pandas as pd

from anomstack.alerts.send import send_alert
from anomstack.config import get_specs
from anomstack.df.save import save_df
from anomstack.df.wrangle import wrangle_df
from anomstack.jinja.render import render
from anomstack.llm.agent import detect_anomalies
from anomstack.sql.read import read_sql
from anomstack.validate.validate import validate_df

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_llmalert_job(spec: dict) -> JobDefinition:
    """Builds a job definition for the LLM Alert job.

    Args:
        spec (dict): A dictionary containing the specifications for the job.

    Returns:
        JobDefinition: A job definition for the LLM Alert job.
    """

    logger = get_dagster_logger()

    if spec.get("disable_llmalert"):

        @job(
            name=f'{spec["metric_batch"]}_llmalert_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    metric_batch = spec["metric_batch"]
    db = spec["db"]
    table_key = spec["table_key"]
    threshold = spec["alert_threshold"]
    alert_methods = spec["alert_methods"]
    llmalert_recent_n = spec["llmalert_recent_n"]
    llmalert_smooth_n = spec["llmalert_smooth_n"]
    llmalert_metric_rounding = spec.get("llmalert_metric_rounding", -1)
    llmalert_prompt_max_n = spec.get("llmalert_prompt_max_n", 1000)
    # Support both new and legacy parameter names for backward compatibility
    # If no custom prompts are specified, defaults to None to use anomaly-agent's built-in defaults
    detection_prompt = spec.get("llmalert_anomaly_agent_detection_prompt") or spec.get(
        "llmalert_anomaly_agent_system_prompt"
    )
    verification_prompt = spec.get("llmalert_anomaly_agent_verification_prompt")

    @job(
        name=f"{metric_batch}_llmalert_job",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        A job that runs the LLM Alert.
        """

        @op(name=f"{metric_batch}_get_llmalert_data")
        def get_llmalert_data() -> pd.DataFrame:
            """An operation that retrieves the data for the LLM Alert.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for the LLM Alert.
            """

            df = read_sql(render("llmalert_sql", spec), db)

            return df

        @op(name=f"{metric_batch}_llmalert")
        def llmalert(context, df: pd.DataFrame) -> pd.DataFrame:
            """An operation that runs the LLM Alert.

            Args:
                context: The context of the operation.
                df (pd.DataFrame): A pandas DataFrame containing the data for
                    the LLM Alert.

            Returns:
                None
            """

            df_alerts = pd.DataFrame()

            for metric_name in df["metric_name"].unique():
                df_metric = (
                    df[df.metric_name == metric_name]
                    .sort_values("metric_timestamp", ascending=True)
                    .reset_index(drop=True)
                )
                df_metric = df_metric.dropna()
                df_metric["metric_timestamp"] = pd.to_datetime(df_metric["metric_timestamp"])

                if llmalert_smooth_n > 0:
                    df_metric["metric_value"] = (
                        df_metric["metric_value"].rolling(llmalert_smooth_n).mean()
                    )

                # logger.debug(f"df_metric: \n{df_metric}")

                df_prompt = (
                    (df_metric[["metric_timestamp", "metric_value"]].dropna())
                    .sort_values("metric_timestamp")
                    .tail(llmalert_prompt_max_n)
                )
                df_prompt["metric_timestamp"] = df_prompt["metric_timestamp"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if llmalert_metric_rounding >= 0:
                    df_prompt = df_prompt.round(llmalert_metric_rounding)

                # logger.debug(f"detection_prompt: \n{detection_prompt}")
                df_detected_anomalies = detect_anomalies(
                    df_prompt, detection_prompt, verification_prompt
                )
                logger.debug(
                    f"Raw anomaly detection output columns: {df_detected_anomalies.columns.tolist()}"
                )
                logger.debug(f"Raw anomaly detection output shape: {df_detected_anomalies.shape}")

                df_detected_anomalies = df_detected_anomalies.rename(
                    columns={
                        "timestamp": "anomaly_timestamp",
                        "anomaly_description": "anomaly_explanation",
                    }
                )
                logger.debug(
                    f"After rename - anomaly detection columns: {df_detected_anomalies.columns.tolist()}"
                )

                num_anomalies_total = len(df_detected_anomalies)
                logger.debug(f"{num_anomalies_total} total anomalies detected in {metric_name}")

                if num_anomalies_total == 0:
                    df_alerts = pd.DataFrame()
                else:
                    # ensure both columns are datetime64[ns] type before merging
                    df_metric["metric_timestamp"] = df_metric["metric_timestamp"].dt.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    df_detected_anomalies["anomaly_timestamp"] = df_detected_anomalies[
                        "anomaly_timestamp"
                    ].dt.strftime("%Y-%m-%d %H:%M:%S")

                    # merge the two dataframes on the metric_timestamp column
                    logger.debug(f"Before merge - df_metric columns: {df_metric.columns.tolist()}")
                    logger.debug(
                        f"Before merge - df_detected_anomalies columns: {df_detected_anomalies.columns.tolist()}"
                    )

                    df_metric = df_metric.merge(
                        df_detected_anomalies,
                        how="left",
                        left_on="metric_timestamp",
                        right_on="anomaly_timestamp",
                    )
                    logger.debug(f"After merge - df_metric columns: {df_metric.columns.tolist()}")
                    logger.debug(f"After merge - df_metric shape: {df_metric.shape}")

                    df_metric["metric_timestamp"] = pd.to_datetime(
                        df_metric["metric_timestamp"], format="%Y-%m-%d %H:%M:%S"
                    )

                    # if there are detected anomalies set metric_alert to 1
                    df_metric["metric_alert"] = df_metric["anomaly_timestamp"].notnull().astype(int)

                    num_anomalies_recent = df_metric["metric_alert"].tail(llmalert_recent_n).sum()

                    logger.debug(
                        f"{num_anomalies_recent} anomalies detected in the last {llmalert_recent_n} rows of {metric_name}"
                    )

                    # if any anomalies were detected in llmaltert_recent_n rows of df_metric then send an alert
                    if num_anomalies_recent > 0:
                        latest_anomaly_timestamp = df_metric[
                            df_metric["anomaly_timestamp"].notnull()
                        ]["anomaly_timestamp"].max()
                        # prefix each explanation with the timestamp
                        if "anomaly_explanation" in df_metric.columns:
                            anomaly_df = df_metric[df_metric["anomaly_timestamp"].notnull()][
                                ["anomaly_timestamp", "anomaly_explanation"]
                            ]
                            anomaly_explanations = anomaly_df.apply(
                                lambda x: f"- {x[0]}: {x[1]}", axis=1
                            ).sort_values(ascending=False)
                        else:
                            logger.warning(
                                f"anomaly_explanation column missing for {metric_name}, using generic message"
                            )
                            anomaly_explanations = pd.Series(
                                [f"- {latest_anomaly_timestamp}: Anomaly detected"]
                            )
                        anomaly_explanations = anomaly_explanations.head(llmalert_recent_n)
                        anomaly_explanations = "\n".join(anomaly_explanations)
                        metric_timestamp_max = df_metric["metric_timestamp"].max()
                        alert_title = (
                            f"🤖 LLM says [{metric_name}] looks anomalous "
                            f"({latest_anomaly_timestamp}) 🤖"
                        )

                        # Wrap send_alert in try-except to prevent blocking save_llmalerts
                        try:
                            df_metric = send_alert(
                                metric_name=metric_name,
                                title=alert_title,
                                df=df_metric,
                                threshold=threshold,
                                alert_methods=alert_methods,
                                description=anomaly_explanations,
                                tags={
                                    "metric_batch": metric_batch,
                                    "metric_name": metric_name,
                                    "anomaly_timestamp": latest_anomaly_timestamp,
                                    "metric_timestamp_max": metric_timestamp_max,
                                    "alert_type": "llm",
                                },
                                score_col="metric_score",
                            )
                            logger.info(f"successfully sent LLM alert for {metric_name}")
                        except Exception as e:
                            logger.error(f"failed to send LLM alert for {metric_name}: {str(e)}")
                            # Continue processing even if alert sending fails

                        # append the alerts to the df_alerts
                        df_alerts = pd.concat([df_alerts, df_metric])

            return df_alerts

        @op(name=f"{metric_batch}_save_llmalerts")
        def save_llmalerts(df_alerts: pd.DataFrame) -> pd.DataFrame:
            """
            Save alerts to db.

            Args:
                df (DataFrame): A pandas DataFrame containing the alerts to be saved.

            Returns:
                DataFrame: A pandas DataFrame containing the saved alerts.
            """

            if df_alerts.empty:
                logger.info("no alerts to save")
                return df_alerts

            df_alerts = df_alerts.query("metric_alert == 1")

            if len(df_alerts) > 0:
                df_alerts["metric_type"] = "llmalert"
                df_alerts["metric_alert"] = df_alerts["metric_alert"].astype(float)
                df_alerts["metric_value"] = df_alerts["metric_alert"]
                if "anomaly_explanation" in df_alerts.columns:
                    df_alerts["metadata"] = df_alerts["anomaly_explanation"].apply(
                        lambda x: (json.dumps({"anomaly_explanation": x}) if pd.notna(x) else None)
                    )
                else:
                    df_alerts["metadata"] = None
                # Explicitly select columns to ensure DataFrame type
                columns_to_keep = [
                    "metric_timestamp",
                    "metric_batch",
                    "metric_name",
                    "metric_type",
                    "metric_value",
                    "metadata",
                ]
                df_alerts = df_alerts.loc[:, columns_to_keep].copy()
                df_alerts = wrangle_df(df_alerts)
                df_alerts = validate_df(df_alerts)
                logger.info(f"saving {len(df_alerts)} llmalerts to {db} {table_key}")
                df_alerts = save_df(df_alerts, db, table_key)

            return df_alerts

        # Restructured job flow: save_llmalerts depends on llmalert output
        df_data = get_llmalert_data()
        df_alerts = llmalert(df_data)
        save_llmalerts(df_alerts)

    return _job


# Build llmalert jobs and schedules.
llmalert_jobs = []
llmalert_schedules = []
specs = get_specs()
for spec_name, spec in specs.items():
    llmalert_job = build_llmalert_job(spec)
    llmalert_jobs.append(llmalert_job)
    if spec["llmalert_default_schedule_status"] == "RUNNING":
        llmalert_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        llmalert_default_schedule_status = DefaultScheduleStatus.STOPPED
    llmalert_schedule = ScheduleDefinition(
        job=llmalert_job,
        cron_schedule=spec["llmalert_cron_schedule"],
        default_status=llmalert_default_schedule_status,
    )
    llmalert_schedules.append(llmalert_schedule)
