"""
Some utility functions.
"""

from dagster import get_dagster_logger
import pandas as pd
import jinja2
from jinja2 import FileSystemLoader
import requests
import json
import os
import duckdb


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


def read_sql_bigquery(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    
    logger.info(f'sql:\n{sql}')
    df = pd.read_gbq(query=sql)
    logger.info(f'df:\n{df}')
    
    return df


def read_sql_duckdb(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    
    logger.info(f'sql:\n{sql}')
    df = duckdb.sql(sql).df()
    logger.info(f'df:\n{df}')
    
    return df


def read_sql(sql, db) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    
    logger.info(f'sql:\n{sql}')
    if db=='bigquery':
        df = read_sql_bigquery(sql)
    elif db=='duckdb':
        df = read_sql_duckdb(sql)
    else:
        raise ValueError(f'Unknown db: {db}')
    logger.info(f'df:\n{df}')
    
    return df


def save_df_bigquery(df, table_key, project_id, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """

    df.to_gbq(
        destination_table=table_key,
        project_id=project_id,
        if_exists=if_exists,
    )
    
    return df


def save_df_duckdb(df, table_key) -> pd.DataFrame:
    """
    Save df to db.
    """

    try:
        if '.' in table_key:
            schema, _ = table_key.split('.')
            duckdb.sql(f'CREATE SCHEMA IF NOT EXISTS {schema}')
        duckdb.sql(f'INSERT INTO {table_key} SELECT * FROM df')
    except:
        duckdb.sql(f'CREATE TABLE {table_key} AS SELECT * FROM df')
    
    return df


def save_df(df, db, table_key, project_id, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """

    if db=='bigquery':
        df = save_df_bigquery(df, table_key, project_id, if_exists)
    elif db=='duckdb':
        df = save_df_duckdb(df, table_key)
    else:
        raise ValueError(f'Unknown db: {db}')
    
    return df


def send_alert_webhook(title='alert', message='hello', env_var_webhook_url='ANOMSTACK_SLACK_WEBHOOK_URL') -> requests.Response:
    """
    Send alert via webhook.
    """
    
    webhook_url = os.environ[env_var_webhook_url]
    payload = {
        'text': f'{title}\n{message}'
        }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    
    return response
    

def send_alert(title, df) -> pd.DataFrame:
    """
    Send alert.
    """
    
    logger = get_dagster_logger()
    logger.info(f'alerts to send: \n{df}')
    _ = send_alert_webhook(title=title, message=df.to_string())
    
    return df
