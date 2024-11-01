"""
Generate plot jobs and schedules.
"""

import base64
import os
from io import BytesIO

import pandas as pd
from dagster import (
    MAX_RUNTIME_SECONDS_TAG,
    DefaultScheduleStatus,
    JobDefinition,
    MetadataValue,
    ScheduleDefinition,
    asset,
    job,
    op,
)

from anomstack.config import specs
from anomstack.df.resample import resample
from anomstack.jinja.render import render
from anomstack.plots.plot import make_batch_plot
from anomstack.sql.read import read_sql

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv(
    "ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600
)


def build_plot_job(spec: dict) -> JobDefinition:
    """Builds a plot job based on the given specification.

    Args:
        spec (dict): The specification for the plot job.

    Returns:
        JobDefinition: The plot job definition.
    """

    if spec.get("disable_plot"):

        @job(
            name=f'{spec["metric_batch"]}_plot_disabled',
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
    preprocess_params = spec["preprocess_params"]
    freq = preprocess_params.get("freq")
    freq_agg = preprocess_params.get("freq_agg")

    @job(
        name=f"{metric_batch}_plot_job",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """The main plot job."""

        @op(name=f"{metric_batch}_get_plot_data")
        def get_plot_data() -> pd.DataFrame:
            """Gets the plot data.

            Returns:
                pd.DataFrame: The plot data.
            """

            sql = render("plot_sql", spec)
            df = read_sql(sql, db)
            df["metric_alert"] = df["metric_alert"].fillna(0)
            if "metric_change" in df.columns:
                df["metric_change"] = df["metric_change"].fillna(0)

            if freq:
                df = resample(df, freq, freq_agg)

            return df

        @asset(name=f"{metric_batch}_plot")
        def make_plot(context, df: pd.DataFrame) -> None:
            """Generates the plot.

            Args:
                context (AssetExecutionContext): The asset execution context.
                df (pd.DataFrame): The plot data.
            """

            fig = make_batch_plot(df)

            buffer = BytesIO()
            fig.savefig(buffer, format="png")
            image_data = base64.b64encode(buffer.getvalue())
            md_content = f"![img](data:image/png;base64,{image_data.decode()})"

            context.add_output_metadata({"plot": MetadataValue.md(md_content)})

        make_plot(get_plot_data())

    return _job


# Build plot jobs and schedules.
plot_jobs = []
plot_schedules = []
for spec_name, spec in specs.items():
    plot_job = build_plot_job(spec)
    plot_jobs.append(plot_job)
    if spec["plot_default_schedule_status"] == "RUNNING":
        plot_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        plot_default_schedule_status = DefaultScheduleStatus.STOPPED
    plot_schedule = ScheduleDefinition(
        job=plot_job,
        cron_schedule=spec["plot_cron_schedule"],
        default_status=plot_default_schedule_status,
    )
    plot_schedules.append(plot_schedule)
