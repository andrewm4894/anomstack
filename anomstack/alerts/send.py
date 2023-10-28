"""
Helper functions to send alerts.
"""

from dagster import get_dagster_logger
import pandas as pd
from anomstack.alerts.asciiart import make_alert_message
from anomstack.alerts.slack import send_alert_slack
from anomstack.alerts.email import send_email_with_plot


def send_alert(
    metric_name: str,
    title: str,
    df: pd.DataFrame,
    alert_methods: str = "email,slack",
    threshold: float = 0.8,
    description: str = "",
) -> pd.DataFrame:
    """
    Sends an alert using the specified alert methods.

    Args:
        metric_name (str): The name of the metric.
        title (str): The title of the alert.
        df (pd.DataFrame): The data to be included in the alert.
        alert_methods (str, optional): The alert methods to use, separated by commas. Defaults to 'email,slack'.
        threshold (float, optional): The threshold for the alert. Defaults to 0.8.

    Returns:
        pd.DataFrame: The input DataFrame.
    """
    logger = get_dagster_logger()
    logger.info(f"alerts to send: \n{df}")
    message = make_alert_message(df, description=description)
    if "slack" in alert_methods:
        send_alert_slack(title=title, message=message)
    if "email" in alert_methods:
        send_email_with_plot(
            df=df,
            metric_name=metric_name,
            subject=title,
            body=message,
            attachment_name=metric_name,
            threshold=threshold,
        )

    return df
