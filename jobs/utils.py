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
from google.oauth2.service_account import Credentials


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


def read_sql(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    
    #logger.info(f'os.environ:\n{os.environ}')
    
    credentials = Credentials.from_service_account_file('/gcp_credentials.json')
    #credentials = Credentials.from_service_account_file(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    
    logger.info(f'sql:\n{sql}')
    df = pd.read_gbq(query=sql, credentials=credentials)
    logger.info(f'df:\n{df}')
    
    return df


def save_df(df, table_key, project_id, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """
    credentials = Credentials.from_service_account_file('/gcp_credentials.json')
    df.to_gbq(
        destination_table=table_key,
        project_id=project_id,
        if_exists=if_exists,
        credentials=credentials,
    )
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
