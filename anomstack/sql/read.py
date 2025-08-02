"""
This module provides functions for reading data from SQL databases using
different database connectors.
"""

from dagster import get_dagster_logger
import pandas as pd

from anomstack.df.utils import log_df_info
from anomstack.external.clickhouse.clickhouse import (
    read_sql_clickhouse,
    run_sql_clickhouse,
)
from anomstack.external.duckdb.duckdb import read_sql_duckdb, run_sql_duckdb
from anomstack.external.gcp.bigquery import read_sql_bigquery
from anomstack.external.prometheus.prometheus import read_sql_prometheus
from anomstack.external.snowflake.snowflake import read_sql_snowflake
from anomstack.external.sqlite.sqlite import read_sql_sqlite, run_sql_sqlite
from anomstack.sql.translate import db_translate
import re
from jinja2 import Template

pd.options.display.max_columns = 10


def _read_sql_prometheus_converted(sql: str, logger) -> pd.DataFrame:
    """
    Convert SQL patterns to PromQL queries using dedicated Prometheus query functions.
    
    This detects the job type and calls the appropriate Prometheus query function
    which handles PromQL construction and SQL-equivalent post-processing.
    
    Args:
        sql: SQL query (typically from Jinja template)
        logger: Dagster logger
        
    Returns:
        pd.DataFrame: Query results in expected format
    """
    from anomstack.config import get_specs
    from anomstack.external.prometheus import (
        execute_prometheus_train_query,
        execute_prometheus_score_query, 
        execute_prometheus_alert_query,
        execute_prometheus_change_query,
        execute_prometheus_llmalert_query
    )
    
    logger.info("Converting SQL to Prometheus query using dedicated functions")
    
    # Detect job type from SQL patterns
    job_type = None
    if "metric_type = 'metric'" in sql:
        if "metric_recency_rank" in sql:
            job_type = "train"
        else:
            job_type = "score"
    elif "metric_type = 'score'" in sql:
        job_type = "alerts"
    else:
        # Try to detect from common SQL patterns
        if "train_max_n" in sql or "train_min_n" in sql:
            job_type = "train"
        elif "score_" in sql:
            job_type = "score"  
        elif "alert_" in sql:
            job_type = "alerts"
        elif "change_" in sql:
            job_type = "change"
        elif "llmalert_" in sql:
            job_type = "llmalert"
        else:
            job_type = "train"  # Default fallback
    
    logger.info(f"Detected job type: {job_type}")
    
    # Get the current spec context
    try:
        specs = get_specs()
        spec = specs[0] if specs else {}  # Use first spec as fallback
    except Exception as e:
        logger.warning(f"Failed to get specs: {e}")
        spec = {}
    
    # Call appropriate Prometheus query function
    try:
        if job_type == "train":
            return execute_prometheus_train_query(spec)
        elif job_type == "score":
            return execute_prometheus_score_query(spec)
        elif job_type == "alerts":
            return execute_prometheus_alert_query(spec)
        elif job_type == "change":
            return execute_prometheus_change_query(spec)
        elif job_type == "llmalert":
            return execute_prometheus_llmalert_query(spec)
        else:
            logger.warning(f"Unknown job type: {job_type}, falling back to train query")
            return execute_prometheus_train_query(spec)
            
    except Exception as e:
        logger.error(f"Failed to execute Prometheus {job_type} query: {e}")
        # Return empty DataFrame with expected columns
        empty_df = pd.DataFrame()
        empty_df["metric_timestamp"] = pd.Series(dtype="datetime64[ns]")
        empty_df["metric_name"] = pd.Series(dtype="string")
        empty_df["metric_value"] = pd.Series(dtype="float64")
        empty_df["metric_batch"] = pd.Series(dtype="string")
        empty_df["metric_type"] = pd.Series(dtype="string")
        return empty_df


def read_sql(sql: str, db: str, returns_df: bool = True) -> pd.DataFrame:
    """
    Read data from SQL.

    Args:
        sql (str): SQL query to execute.
        db (str): Name of the database to connect to.
        returns_df (bool, optional): Whether the query expects a DataFrame as a result.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the results of the SQL query.
    """

    logger = get_dagster_logger()

    # For Prometheus, convert SQL patterns to PromQL instead of translating
    if db == "prometheus":
        return _read_sql_prometheus_converted(sql, logger)
    
    sql = db_translate(sql, db)

    logger.debug(f"-- read_sql() is about to read this qry:\n{sql}")

    df = pd.DataFrame()  # Initialize df to avoid unbound variable error

    if db == "bigquery":
        if returns_df:
            df = read_sql_bigquery(sql)
        elif not returns_df:
            raise NotImplementedError("BigQuery not yet implemented for non-returns_df queries.")
    elif db == "snowflake":
        if returns_df:
            df = read_sql_snowflake(sql)
        elif not returns_df:
            raise NotImplementedError("Snowflake not yet implemented for non-returns_df queries.")
    elif db == "duckdb":
        if returns_df:
            df = read_sql_duckdb(sql)
        elif not returns_df:
            run_sql_duckdb(sql)
            df = pd.DataFrame()
    elif db == "sqlite":
        if returns_df:
            df = read_sql_sqlite(sql)
        elif not returns_df:
            run_sql_sqlite(sql)
            df = pd.DataFrame()
    elif db == "clickhouse":
        if returns_df:
            df = read_sql_clickhouse(sql)
        elif not returns_df:
            run_sql_clickhouse(sql)
            df = pd.DataFrame()
    elif db == "prometheus":
        if returns_df:
            # For Prometheus, sql parameter actually contains PromQL
            df = read_sql_prometheus(sql)
        elif not returns_df:
            # Prometheus doesn't support non-returning queries in this context
            raise NotImplementedError("Prometheus not yet implemented for non-returns_df queries.")
    else:
        raise ValueError(f"Unknown db: {db}")

    log_df_info(df, logger)
    logger.debug(f"df.head():\n{df.head()}")
    logger.debug(f"df.tail():\n{df.tail()}")

    return df
