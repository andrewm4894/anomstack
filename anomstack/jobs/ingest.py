"""
Generate ingest jobs and schedules.
"""

import os
import json
from typing import Dict

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

from anomstack.config import get_specs
from anomstack.df.save import save_df
from anomstack.df.wrangle import wrangle_df
from anomstack.fn.run import run_df_fn
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.validate.validate import validate_df
from anomstack.ml.threshold import detect_threshold_alerts
from anomstack.alerts.send import send_alert

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_ingest_job(spec: Dict) -> JobDefinition:
    """
    Build job definitions for ingest jobs.

    Args:
        spec (Dict): A dictionary containing the specifications for the job.

    Returns:
        JobDefinition: A job definition for the ingest job.
    """

    if spec.get("disable_ingest"):

        @job(
            name=f'{spec["metric_batch"]}_ingest_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    metric_batch = spec["metric_batch"]
    table_key = spec["table_key"]
    db = spec["db"]
    ingest_sql = spec.get("ingest_sql")
    ingest_fn = spec.get("ingest_fn")
    ingest_metric_rounding = spec.get("ingest_metric_rounding", 4)
    
    # Threshold alert configuration
    disable_tholdalert = spec.get("disable_tholdalert", True)
    tholdalert_thresholds = spec.get("tholdalert_thresholds", {})
    tholdalert_methods = spec.get("tholdalert_methods", "email,slack")
    tholdalert_recent_n = spec.get("tholdalert_recent_n", 1)
    tholdalert_snooze_n = spec.get("tholdalert_snooze_n", 3)
    tholdalert_exclude_metrics = spec.get("tholdalert_exclude_metrics", [])
    metric_tags = spec.get("metric_tags", {})

    @job(
        name=f"{metric_batch}_ingest",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Run SQL to calculate metrics and save to db.
        """

        @op(name=f"{metric_batch}_create_metrics")
        def create_metrics() -> pd.DataFrame:
            """
            Calculate metrics.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the calculated metrics.
            """
            if ingest_sql:
                df = read_sql(render("ingest_sql", spec), db)
            elif ingest_fn:
                df = run_df_fn("ingest", render("ingest_fn", spec))
            else:
                raise ValueError(
                    f"No ingest_sql or ingest_fn specified for {metric_batch}."
                )
            logger.debug(f"df: \n{df}")
            df["metric_batch"] = metric_batch
            df["metric_type"] = "metric"
            
            # Add threshold configuration to metadata for metrics with thresholds
            if tholdalert_thresholds:
                def add_threshold_metadata(row):
                    """Add threshold configuration to metadata if it exists for this metric."""
                    metadata = {}
                    
                    # Parse existing metadata if it exists
                    if 'metadata' in df.columns and pd.notna(row.get('metadata')) and row.get('metadata'):
                        try:
                            metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else {}
                        except (json.JSONDecodeError, TypeError):
                            metadata = {}
                    
                    # Add threshold configuration if metric has thresholds
                    metric_name = row.get('metric_name')
                    if metric_name and metric_name in tholdalert_thresholds:
                        metadata['thresholds'] = tholdalert_thresholds[metric_name]
                    
                    return json.dumps(metadata) if metadata else ""
                
                df['metadata'] = df.apply(add_threshold_metadata, axis=1)
            
            df = wrangle_df(df, rounding=ingest_metric_rounding)
            df = validate_df(df)

            return df

        @op(name=f"{metric_batch}_save_metrics")
        def save_metrics(df: pd.DataFrame) -> pd.DataFrame:
            """
            Save metrics to db.

            Args:
                df (pd.DataFrame): A pandas DataFrame containing the metrics
                    to be saved.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the saved metrics.
            """
            df = save_df(df, db, table_key)

            return df

        # Threshold alert operations (run in parallel with save_metrics if enabled)
        @op(name=f"{metric_batch}_detect_threshold_alerts")
        def detect_tholdalerts(df: pd.DataFrame) -> pd.DataFrame:
            """
            Detect threshold-based alerts.

            Args:
                df (pd.DataFrame): A pandas DataFrame containing the metrics.

            Returns:
                pd.DataFrame: A pandas DataFrame with threshold alert indicators.
            """
            if disable_tholdalert or not tholdalert_thresholds:
                logger.info("Threshold alerts disabled or no thresholds configured")
                return pd.DataFrame()

            # Filter out excluded metrics
            if tholdalert_exclude_metrics:
                df_filtered = df[~df['metric_name'].isin(tholdalert_exclude_metrics)].copy()
            else:
                df_filtered = df.copy()

            df_threshold_alerts = detect_threshold_alerts(
                df_filtered, 
                tholdalert_thresholds, 
                tholdalert_recent_n, 
                tholdalert_snooze_n
            )

            return df_threshold_alerts

        @op(name=f"{metric_batch}_tholdalert_op")
        def tholdalert(df_threshold_alerts: pd.DataFrame) -> pd.DataFrame:
            """
            Send threshold alerts.

            Args:
                df_threshold_alerts (pd.DataFrame): A pandas DataFrame containing threshold alerts.

            Returns:
                pd.DataFrame: A pandas DataFrame containing the threshold alerts.
            """
            if disable_tholdalert or df_threshold_alerts.empty:
                logger.info("No threshold alerts to send")
                return df_threshold_alerts

            alerts_to_send = df_threshold_alerts[df_threshold_alerts['threshold_alert'] == 1]
            
            if len(alerts_to_send) == 0:
                logger.info("No threshold alerts to send")
            else:
                # Convert to proper DataFrame to ensure type consistency
                alerts_to_send = pd.DataFrame(alerts_to_send)
                
                for metric_name in alerts_to_send['metric_name'].unique():
                    logger.info(f"sending threshold alert for {metric_name}")
                    df_alert = alerts_to_send[alerts_to_send['metric_name'] == metric_name].copy()
                    
                    # Ensure df_alert is a proper DataFrame
                    if not isinstance(df_alert, pd.DataFrame):
                        df_alert = pd.DataFrame(df_alert)
                    
                    df_alert['metric_timestamp'] = pd.to_datetime(df_alert['metric_timestamp'])
                    
                    metric_timestamp_max = df_alert['metric_timestamp'].max().strftime("%Y-%m-%d %H:%M")
                    threshold_type = df_alert['threshold_type'].iloc[0]
                    threshold_value = df_alert['threshold_value'].iloc[0]
                    metric_value = df_alert['metric_value'].iloc[0]
                    
                    alert_title = f"⚠️ [{metric_name}] threshold {threshold_type} bound breached ({metric_timestamp_max}) ⚠️"
                    
                    tags = {
                        "metric_batch": metric_batch,
                        "metric_name": metric_name,
                        "metric_timestamp": metric_timestamp_max,
                        "alert_type": "threshold",
                        "threshold_type": threshold_type,
                        "threshold_value": threshold_value,
                        "metric_value": metric_value,
                        **metric_tags.get(metric_name, {}),
                    }
                    logger.debug(f"threshold alert tags:\n{tags}")
                    
                    # Wrap send_alert in try-except to prevent blocking save_tholdalerts
                    try:
                        df_alert = send_alert(
                            metric_name=metric_name,
                            title=alert_title,
                            df=df_alert,
                            threshold=threshold_value,
                            alert_methods=tholdalert_methods,
                            tags=tags,
                            metric_timestamp=metric_timestamp_max
                        )
                        logger.info(f"successfully sent threshold alert for {metric_name}")
                    except Exception as e:
                        logger.error(f"failed to send threshold alert for {metric_name}: {str(e)}")
                        # Continue processing other metrics even if one fails

            return df_threshold_alerts

        @op(name=f"{metric_batch}_save_tholdalerts")
        def save_tholdalerts(df_threshold_alerts: pd.DataFrame) -> pd.DataFrame:
            """
            Save threshold alerts to db.

            Args:
                df_threshold_alerts (DataFrame): A pandas DataFrame containing the threshold alerts to be saved.

            Returns:
                DataFrame: A pandas DataFrame containing the saved threshold alerts.
            """
            if disable_tholdalert or df_threshold_alerts.empty:
                logger.info("No threshold alerts to save")
                return df_threshold_alerts

            df_alerts = df_threshold_alerts[df_threshold_alerts['threshold_alert'] == 1].copy()

            if len(df_alerts) > 0:
                df_alerts["metric_type"] = "tholdalert"
                df_alerts["metric_alert"] = df_alerts["threshold_alert"].astype(float)
                
                # Add threshold metadata to alert records
                def add_threshold_alert_metadata(row):
                    """Add threshold configuration and alert details to metadata."""
                    metadata = {}
                    
                    metric_name = row.get('metric_name')
                    if metric_name and metric_name in tholdalert_thresholds:
                        metadata['thresholds'] = tholdalert_thresholds[metric_name]
                        
                        # Add details about which threshold was breached
                        if pd.notna(row.get('threshold_type')):
                            metadata['breached_threshold_type'] = row['threshold_type']
                        if pd.notna(row.get('threshold_value')):
                            metadata['breached_threshold_value'] = row['threshold_value']
                        if pd.notna(row.get('metric_value')):
                            metadata['metric_value_at_breach'] = row['metric_value']
                    
                    return json.dumps(metadata) if metadata else ""
                
                df_alerts['metadata'] = df_alerts.apply(add_threshold_alert_metadata, axis=1)
                
                # Explicitly select columns to ensure DataFrame type
                columns_to_keep = [
                    "metric_timestamp",
                    "metric_batch", 
                    "metric_name",
                    "metric_type",
                    "metric_alert",
                    "metadata",
                ]
                df_alerts = df_alerts.loc[:, columns_to_keep].copy()
                df_alerts = df_alerts.rename(columns={"metric_alert": "metric_value"})
                df_alerts = wrangle_df(df_alerts)
                df_alerts = validate_df(df_alerts)
                logger.info(f"saving {len(df_alerts)} threshold alerts to {db} {table_key}")
                df_alerts = save_df(df_alerts, db, table_key)
            else:
                logger.info("no threshold alerts to save")

            # Ensure we return a proper DataFrame
            if not isinstance(df_alerts, pd.DataFrame):
                df_alerts = pd.DataFrame(df_alerts)
            return df_alerts

        # Main job flow - metrics saved normally, threshold alerts processed in parallel
        df_metrics = create_metrics()
        save_metrics(df_metrics)
        
        # Threshold alert flow (only runs if enabled)
        if not disable_tholdalert and tholdalert_thresholds:
            df_threshold_alerts = detect_tholdalerts(df_metrics)
            tholdalert(df_threshold_alerts)
            save_tholdalerts(df_threshold_alerts)

    return _job


logger = get_dagster_logger()

# Build ingest jobs and schedules.
ingest_jobs = []
ingest_schedules = []
specs = get_specs()
for spec_key, spec in specs.items():
    logger.debug(f"Building ingest job for {spec_key}")
    logger.debug(f"Specs: \n{spec}")
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
