"""
"""

from dagster import get_dagster_logger
import pandas as pd
import jinja2
from jinja2 import FileSystemLoader
from anomstack.utils.bigquery import read_sql_bigquery, save_df_bigquery
from anomstack.utils.duckdb import read_sql_duckdb, save_df_duckdb


def render_sql(sql_key, spec, params=None) -> str:
    """
    Render SQL from template.
    """
    
    environment = jinja2.Environment(loader=FileSystemLoader('metrics/'))
    
    if params is None:
        params = {}
    
    sql = environment.from_string(spec[sql_key])
    sql = sql.render(
        table_key=spec.get('table_key'),
        metric_batch=spec.get('metric_batch'),
        train_max_n=spec.get('train_max_n'),
        score_max_n=spec.get('score_max_n'),
        alert_max_n=spec.get('alert_max_n'),
        alert_threshold=spec.get('alert_threshold'),
        alert_smooth_n=spec.get('alert_smooth_n'),
        metric_name=params.get('metric_name'),
    )
    
    return sql
