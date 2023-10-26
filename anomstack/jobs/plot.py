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
)
from typing import List, Tuple
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql


def build_plot_job(spec) -> JobDefinition:
    """ """

    metric_batch = spec["metric_batch"]
    db = spec["db"]

    @job(name=f"{metric_batch}_plot_job")
    def _job():
        """ """

        @op(name=f"{metric_batch}_get_plot_data")
        def get_plot_data() -> pd.DataFrame:
            """ """

            df = read_sql(render("plot_sql", spec), db)

            return df

        @asset(name=f"{metric_batch}_plot")
        def make_plot(context, df):
            """ """

            # Filter data for each metric_name and plot
            unique_metrics = df["metric_name"].unique()
            colors = sns.color_palette("viridis", len(unique_metrics))

            # Create the time series plots with metric_score on the second y-axis
            plt.figure(figsize=(15, 5 * len(unique_metrics)))

            for i, metric in enumerate(unique_metrics):
                ax1 = plt.subplot(len(unique_metrics), 1, i + 1)
                metric_data = df[df["metric_name"] == metric]

                # Plot metric_value on the primary y-axis
                sns.lineplot(
                    data=metric_data,
                    x="metric_timestamp",
                    y="metric_value",
                    label="Metric Value",
                    color=colors[i],
                    ax=ax1,
                )
                ax1.set_ylabel("Metric Value")
                ax1.tick_params(axis="y", labelcolor=colors[i])

                # Create a second y-axis for metric_score
                ax2 = ax1.twinx()
                sns.lineplot(
                    data=metric_data,
                    x="metric_timestamp",
                    y="metric_score",
                    label="Metric Score",
                    color=colors[i],
                    linestyle="dashed",
                    ax=ax2,
                )
                ax2.set_ylabel("Metric Score")
                ax2.tick_params(axis="y", labelcolor=colors[i])

                plt.title(f"{metric} - value vs score")
                plt.xlabel("Timestamp")

                # Add legends
                lines, labels = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax2.legend(lines + lines2, labels + labels2, loc="upper left")

            plt.tight_layout()

            # Save the image to a buffer and embed the image into Markdown content for quick view
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
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
