"""
Generate ingest jobs and schedules.
"""

import base64
from io import BytesIO
from typing import Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    job,
    op,
    ScheduleDefinition,
    JobDefinition,
    DefaultScheduleStatus,
    get_dagster_logger,
    asset
)
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.fn.run import run_df_fn
from anomstack.df.save import save_df
from anomstack.validate.ingest import validate_ingest_df


def build_ingest_job(spec: Dict) -> JobDefinition:
    """
    Build job definitions for ingest jobs.

    Args:
        spec (Dict): A dictionary containing the specifications for the job.

    Returns:
        JobDefinition: A job definition for the ingest job.
    """

    metric_batch = spec["metric_batch"]
    table_key = spec["table_key"]
    db = spec["db"]
    ingest_sql = spec.get("ingest_sql")
    ingest_fn = spec.get("ingest_fn")

    @job(name=f"{metric_batch}_ingest")
    def _job():
        """
        Run SQL to calculate metrics and save to db.
        """

        @op(name=f"{metric_batch}_create_metrics")
        def create_metrics() -> pd.DataFrame:
            """
            Calculate metrics.

            Returns:
                DataFrame: A pandas DataFrame containing the calculated metrics.
            """
            if ingest_sql:
                df = read_sql(render("ingest_sql", spec), db)
            elif ingest_fn:
                df = run_df_fn("ingest", render("ingest_fn", spec))
            else:
                raise ValueError(
                    f"No ingest_sql or ingest_fn specified for {metric_batch}."
                )
            df = validate_ingest_df(df)
            df["metric_batch"] = metric_batch
            df["metric_type"] = "metric"
            return df

        @op(name=f"{metric_batch}_save_metrics")
        def save_metrics(df: pd.DataFrame) -> pd.DataFrame:
            """
            Save metrics to db.

            Args:
                df (DataFrame): A pandas DataFrame containing the metrics to be saved.

            Returns:
                DataFrame: A pandas DataFrame containing the saved metrics.
            """
            df = save_df(df, db, table_key)
            return df
        
        @asset(name=f"{metric_batch}_asset", compute_kind="Plot")
        def some_plot(context, df) -> None:
            
            # Generate random data
            date_rng = pd.date_range(start='1/1/2020', end='12/31/2021', freq='M')
            sales_data = np.random.randint(100, 1000, size=(len(date_rng)))

            # Create DataFrame
            df = pd.DataFrame(data={'date': date_rng, 'sales': sales_data})
            df.set_index('date', inplace=True)

            # Plot time series
            plt.figure(figsize=(10,5))
            plt.plot(df.index, df['sales'], marker='o')
            plt.title('Monthly Sales Over Time')
            plt.xlabel('Date')
            plt.ylabel('Sales')
            plt.grid(True)

            # Save the image to a buffer and embed the image into Markdown content for quick view
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            image_data = base64.b64encode(buffer.getvalue())
            md_content = f"![img](data:image/png;base64,{image_data.decode()})"

            # Attach the Markdown content and s3 file path as metadata to the asset
            # Read about more metadata types in https://docs.dagster.io/_apidocs/ops#metadata-types
            context.add_output_metadata({"plot": MetadataValue.md(md_content)})

        some_plot(save_metrics(create_metrics()))

    return _job


logger = get_dagster_logger()

# Build ingest jobs and schedules.
ingest_jobs = []
ingest_schedules = []
for spec_key, spec in specs.items():
    logger.info(f"Building ingest job for {spec_key}")
    logger.info(f"Specs: \n{spec}")
    ingest_job = build_ingest_job(spec)
    ingest_jobs.append(ingest_job)
    if spec.get("ingest_default_schedule_status", "STOPPED") == "RUNNING":
        ingest_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        ingest_default_schedule_status = DefaultScheduleStatus.STOPPED
    ingest_schedule = ScheduleDefinition(
        job=ingest_job,
        cron_schedule=spec["ingest_cron_schedule"],
        default_status=ingest_default_schedule_status,
    )
    ingest_schedules.append(ingest_schedule)
