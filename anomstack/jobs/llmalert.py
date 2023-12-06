"""
Generate llmalert jobs and schedules.
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
from anomstack.fn.run import define_fn
from anomstack.jinja.render import render
from anomstack.llm.completion import get_completion
from anomstack.sql.read import read_sql

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_llmalert_job(spec) -> JobDefinition:
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
    threshold = spec["alert_threshold"]
    alert_methods = spec["alert_methods"]
    llmalert_recent_n = spec["llmalert_recent_n"]
    llmalert_smooth_n = spec["llmalert_smooth_n"]
    llmalert_metric_rounding = spec.get("llmalert_metric_rounding", 4)

    @job(
        name=f"{metric_batch}_llmalert_job",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """A job that runs the LLM Alert.

        Returns:
            None
        """

        @op(name=f"{metric_batch}_get_llmalert_data")
        def get_llmalert_data() -> pd.DataFrame:
            """An operation that retrieves the data for the LLM Alert.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the data for the LLM Alert.
            """

            df = read_sql(render("plot_sql", spec), db)

            return df

        @op(name=f"{metric_batch}_llmalert")
        def llmalert(context, df: pd.DataFrame) -> None:
            """An operation that runs the LLM Alert.

            Args:
                context: The context of the operation.
                df (pd.DataFrame): A pandas DataFrame containing the data for the LLM Alert.

            Returns:
                None
            """

            make_prompt = define_fn(fn_name="make_prompt", fn=render("prompt_fn", spec))

            for metric_name in df["metric_name"].unique():
                df_metric = (
                    df[df.metric_name == metric_name]
                    .sort_values(by="metric_timestamp", ascending=True)
                    .reset_index(drop=True)
                )
                df_metric["metric_alert"] = df_metric["metric_alert"].fillna(0)
                df_metric["metric_score"] = df_metric["metric_score"].fillna(0)
                df_metric["metric_score_smooth"] = df_metric["metric_score_smooth"].fillna(0)
                df_metric = df_metric.dropna()
                df_metric["metric_timestamp"] = pd.to_datetime(
                    df_metric["metric_timestamp"]
                )

                if llmalert_smooth_n > 0:
                    df_metric["metric_value"] = (
                        df_metric["metric_value"].rolling(llmalert_smooth_n).mean()
                    )

                df_metric["metric_recency"] = "baseline"
                df_metric.iloc[
                    -llmalert_recent_n:, df_metric.columns.get_loc("metric_recency")
                ] = "recent"

                # logger.debug(f"df_metric: \n{df_metric}")

                df_prompt = (
                    df_metric[["metric_value", "metric_recency"]]
                    .dropna()
                    .round(llmalert_metric_rounding)
                )

                # logger.debug(f"df_prompt: \n{df_prompt}")

                prompt = make_prompt(df_prompt, llmalert_recent_n)

                logger.debug(f"prompt: \n{prompt}")

                (
                    is_anomalous,
                    decision_reasoning,
                    decision_confidence_level,
                ) = get_completion(prompt)

                logger.info(f"is_anomalous: {is_anomalous}")
                decision_description = (
                    f"{decision_confidence_level.upper()}: {decision_reasoning}"
                )
                logger.info(f"decision_description: {decision_description}")

                if is_anomalous and decision_confidence_level.lower() == "high":
                    metric_timestamp_max = (
                        df_metric["metric_timestamp"].max().strftime("%Y-%m-%d %H:%M")
                    )
                    alert_title = f"🤖 LLM says [{metric_name}] looks anomalous ({metric_timestamp_max}) 🤖"
                    df_metric = send_alert(
                        metric_name=metric_name,
                        title=alert_title,
                        df=df_metric,
                        threshold=threshold,
                        alert_methods=alert_methods,
                        description=decision_description,
                        tags={
                            "metric_batch": metric_batch,
                            "metric_name": metric_name,
                            "metric_timestamp": metric_timestamp_max,
                            "alert_type": "llm",
                        },
                    )

        llmalert(get_llmalert_data())

    return _job


# Build llmalert jobs and schedules.
llmalert_jobs = []
llmalert_schedules = []
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
