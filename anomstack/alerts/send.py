"""
Helper functions to send alerts.
"""

from dagster import get_dagster_logger
import pandas as pd
from anomstack.alerts.asciiart import make_alert_message
from anomstack.alerts.slack import send_alert_slack
from anomstack.alerts.email import send_email_with_plot


def send_alert(metric_name, title, df, threshold=0.8) -> pd.DataFrame:
    """
    Send alert.
    """
    
    logger = get_dagster_logger()
    logger.info(f'alerts to send: \n{df}')
    message = make_alert_message(df)
    #_ = send_alert_slack(title=title, message=message)
    send_email_with_plot(
        df=df, 
        metric_name=metric_name, 
        subject=title, 
        body=message, 
        attachment_name=metric_name,
        threshold=threshold
    )
    
    return df
