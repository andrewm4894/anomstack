"""
Generate timegptalert jobs and schedules.
"""

import os
import pandas as pd
from dagster import (
    job,
    op,
    ScheduleDefinition,
    JobDefinition,
    DefaultScheduleStatus,
    get_dagster_logger,
)
from nixtlats import TimeGPT
from anomstack.config import specs
from anomstack.df.resample import resample
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql


def build_timegptalert_job(spec) -> JobDefinition:
    """Builds a job definition for the TimeGPT Alert job.

    Args:
        spec (dict): A dictionary containing the specifications for the job.

    Returns:
        JobDefinition: A job definition for the TimeGPT Alert job.
    """

    timegpt = TimeGPT(token=os.getenv("ANOMSTACK_TIMEGPT_TOKEN"))

    logger = get_dagster_logger()

    if spec.get("disable_timegptalert"):

        @job(name=f'{spec["metric_batch"]}_timegptalert_disabled')
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_timegptalert_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    metric_batch = spec["metric_batch"]
    db = spec["db"]
    threshold = spec["alert_threshold"]
    alert_methods = spec["alert_methods"]
    timegptalert_recent_n = spec["timegptalert_recent_n"]
    timegptalert_smooth_n = spec["timegptalert_smooth_n"]
    timegptalert_metric_rounding = spec.get("timegptalert_metric_rounding", 4)
    timegptalert_freq = spec.get("timegptalert_freq", "1D")
    timegptalert_freq_agg = spec.get("timegptalert_freq_agg", "mean")

    @job(name=f"{metric_batch}_timegptalert_job")
    def _job():
        """A job that runs the TimeGPT Alert.

        Returns:
            None
        """

        @op(name=f"{metric_batch}_get_timegptalert_data")
        def get_timegptalert_data() -> pd.DataFrame:
            """An operation that retrieves the data for the TimeGPT Alert.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for the TimeGPT Alert.
            """

            df = read_sql(render("timegpt_sql", spec), db)

            return df

        @op(name=f"{metric_batch}_timegptalert")
        def timegptalert(context, df: pd.DataFrame) -> None:
            """An operation that runs the TimeGPT Alert.

            Args:
                context: The context of the operation.
                df (pd.DataFrame): A pandas DataFrame containing the data for the TimeGPT Alert.

            Returns:
                None
            """

            for metric_name in df["metric_name"].unique():
                df_metric = (
                    df[df.metric_name == metric_name]
                    .sort_values(by="metric_timestamp", ascending=True)
                    .reset_index(drop=True)
                ).dropna()
                df_metric["metric_timestamp"] = pd.to_datetime(
                    df_metric["metric_timestamp"]
                )

                if timegptalert_smooth_n > 0:
                    df_metric["metric_value"] = (
                        df_metric["metric_value"]
                        .rolling(timegptalert_smooth_n)
                        .mean()
                    )

                df_metric = resample(
                    df,
                    timegptalert_freq,
                    timegptalert_freq_agg
                )

                timegpt_anomalies_df = timegpt.detect_anomalies(
                    df=df_metric[['metric_timestamp', 'metric_value']].reset_index(drop=True),
                    time_col="metric_timestamp",
                    target_col="metric_value",
                    freq=timegptalert_freq
                )

                logger.info(f"timegpt_anomalies_df: \n{timegpt_anomalies_df}")

        timegptalert(get_timegptalert_data())

    return _job


# Build timegptalert jobs and schedules.
timegptalert_jobs = []
timegptalert_schedules = []
for spec_name, spec in specs.items():
    timegptalert_job = build_timegptalert_job(spec)
    timegptalert_jobs.append(timegptalert_job)
    if spec["timegptalert_default_schedule_status"] == "RUNNING":
        timegptalert_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        timegptalert_default_schedule_status = DefaultScheduleStatus.STOPPED
    timegptalert_schedule = ScheduleDefinition(
        job=timegptalert_job,
        cron_schedule=spec["timegptalert_cron_schedule"],
        default_status=timegptalert_default_schedule_status,
    )
    timegptalert_schedules.append(timegptalert_schedule)
