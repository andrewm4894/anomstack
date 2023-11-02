"""
"""

import base64
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
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.plots.plot import make_batch_plot
from anomstack.df.resample import resample


def build_plot_job(spec) -> JobDefinition:
    """ """

    logger = get_dagster_logger()

    if spec.get("disable_plot"):

        @job(name=f'{spec["metric_batch"]}_plot_disabled')
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    metric_batch = spec["metric_batch"]
    db = spec["db"]
    preprocess_params = spec["preprocess_params"]
    freq = preprocess_params.get('freq')
    freq_agg = preprocess_params.get('freq_agg')

    @job(name=f"{metric_batch}_plot_job")
    def _job():
        """ """

        @op(name=f"{metric_batch}_get_plot_data")
        def get_plot_data() -> pd.DataFrame:
            """ """

            df = read_sql(render("plot_sql", spec), db)

            if freq:
                df = resample(df, freq, freq_agg)

            return df

        @asset(name=f"{metric_batch}_plot")
        def make_plot(context, df: pd.DataFrame) -> None:
            """ """

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
