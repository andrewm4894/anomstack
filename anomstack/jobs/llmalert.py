"""
Generate llmalert jobs and schedules.
"""

import os
import pandas as pd
from dagster import (
    job,
    op,
    ScheduleDefinition,
    JobDefinition,
    DefaultScheduleStatus,
    get_dagster_logger
)
import openai
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.alerts.send import send_alert
from anomstack.llm.completion import get_completion
from anomstack.fn.run import define_fn


def build_llmalert_job(spec) -> JobDefinition:
    """Builds a job definition for the LLM Alert job.

    Args:
        spec (dict): A dictionary containing the specifications for the job.

    Returns:
        JobDefinition: A job definition for the LLM Alert job.
    """

    openai.api_key = os.getenv("ANOMSTACK_OPENAI_KEY")
    openai_model = os.getenv("ANOMSTACK_OPENAI_MODEL", "gpt-3.5-turbo")

    logger = get_dagster_logger()

    if spec.get("disable_llmalert"):

        @job(name=f'{spec["metric_batch"]}_llmalert_disabled')
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

    @job(name=f"{metric_batch}_llmalert_job")
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

            make_prompt = define_fn(
                fn_name="make_prompt", fn=render("prompt_fn", spec)
            )

            for metric_name in df["metric_name"].unique():

                df_metric = df[df.metric_name == metric_name].reset_index(drop=True)
                df_metric = df_metric.sort_values(by="metric_timestamp")
                
                if llmalert_smooth_n > 0:
                    df_metric["metric_value_smooth"] = (
                        df_metric["metric_value"]
                        .rolling(llmalert_smooth_n)
                        .mean()
                    )

                metric_col = "metric_value" if llmalert_smooth_n == 0 else "metric_value_smooth"
                prompt = make_prompt(
                    df_metric[['metric_timestamp', metric_col]],
                    llmalert_recent_n
                )

                is_anomalous, anomaly_description = get_completion(prompt, openai_model)

                logger.info(f"is_anomalous: {is_anomalous}")
                logger.info(f"anomaly_description: {anomaly_description}")

                if is_anomalous:
                    metric_timestamp_max = (
                        df_metric["metric_timestamp"].max().strftime("%Y-%m-%d %H:%M")
                    )
                    alert_title = (
                        f"🤖 LLM says [{metric_name}] looks anomalous ({metric_timestamp_max}) 🤖"
                    )
                    df_metric = send_alert(
                        metric_name=metric_name,
                        title=alert_title,
                        df=df_metric,
                        threshold=threshold,
                        alert_methods=alert_methods,
                        description=anomaly_description,
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
