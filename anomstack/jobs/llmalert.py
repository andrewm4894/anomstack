"""
Generate llmalert jobs and schedules.
"""

import base64
import os
import json
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    job,
    op,
    ScheduleDefinition,
    JobDefinition,
    DefaultScheduleStatus,
    asset,
    get_dagster_logger
)
from typing import List, Tuple
import openai
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.plots.plot import make_batch_plot
from anomstack.alerts.send import send_alert
from anomstack.llm.prompt import make_prompt
from anomstack.llm.completion import get_completion


def build_llmalert_job(spec) -> JobDefinition:
    """Builds a job definition for the LLM Alert job.

    Args:
        spec (dict): A dictionary containing the specifications for the job.

    Returns:
        JobDefinition: A job definition for the LLM Alert job.
    """

    openai.api_key = os.getenv("ANOMSTACK_OPENAI_KEY")

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

            for metric_name in df["metric_name"].unique():

                df_metric = df[df.metric_name == metric_name]
                df_metric_prompt = df_metric[['metric_timestamp', 'metric_value']]

                prompt = make_prompt(df_metric_prompt, llmalert_recent_n, metric_name)

                is_anomalous, anomaly_description = get_completion(prompt)

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
