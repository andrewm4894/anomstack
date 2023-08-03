"""
Some utility functions.
"""

from dagster import get_dagster_logger
import pandas as pd
import requests
import json
import os


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
