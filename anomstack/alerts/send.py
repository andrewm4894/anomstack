"""
Helper functions to send alerts.
"""

from dagster import get_dagster_logger
import pandas as pd

from anomstack.alerts.asciiart import make_alert_message
from anomstack.alerts.email import send_email, send_email_with_plot
from anomstack.alerts.slack import send_alert_slack, send_alert_slack_with_plot


def send_alert(
    metric_name: str,
    title: str,
    df: pd.DataFrame,
    alert_methods: str = "email,slack",
    threshold: float = 0.8,
    description: str = "",
    tags=None,
    score_col: str = "metric_score_smooth",
    metric_timestamp=None,
    score_title="anomaly_score",
) -> pd.DataFrame:
    """
    Sends an alert using the specified alert methods.

    Args:
        metric_name (str): The name of the metric.
        title (str): The title of the alert.
        df (pd.DataFrame): The data to be included in the alert.
        alert_methods (str, optional): The alert methods to use, separated by
            commas. Defaults to 'email,slack'.
        threshold (float, optional): The threshold for the alert.
            Defaults to 0.8.
        description (str, optional): The description of the alert.
            Defaults to ''.
        tags (list, optional): The tags to be included in the alert.
            Defaults to None.
        score_col (str, optional): The column name of the score.
            Defaults to 'metric_score_smooth'.
        metric_timestamp (str, optional): The timestamp of the metric.

    Returns:
        pd.DataFrame: The input DataFrame.
    """
    logger = get_dagster_logger()
    logger.debug(f"alerts to send: \n{df}")
    message = make_alert_message(df, description=description, tags=tags, score_col=score_col)
    if "slack" in alert_methods:
        send_alert_slack_with_plot(
            df=df,
            metric_name=metric_name,
            title=title,
            message=description,
            threshold=threshold,
            score_col=score_col,
            metric_timestamp=metric_timestamp,
            score_title=score_title,
            tags=tags,
        )
    if "email" in alert_methods:
        send_email_with_plot(
            df=df,
            metric_name=metric_name,
            subject=title,
            body=message,
            attachment_name=metric_name,
            threshold=threshold,
            score_col=score_col,
            score_title=score_title,
            tags=tags,
        )

    return df


def send_df(
    title: str,
    df: pd.DataFrame,
    alert_methods: str = "email,slack",
    description: str = "",
) -> pd.DataFrame:
    """
    Sends a df using the specified alert methods.

    Args:
        title (str): The title of the alert.
        df (pd.DataFrame): The data to be included in the alert.
        alert_methods (str, optional): The alert methods to use, separated by
            commas. Defaults to 'email,slack'.
        description (str, optional): The description of the alert.
            Defaults to ''.
        tags (list, optional): The tags to be included in the alert.
            Defaults to None.

    Returns:
        pd.DataFrame: The input DataFrame.
    """
    logger = get_dagster_logger()
    logger.debug(f"alerts to send: \n{df}")
    message = df.to_html()
    if "slack" in alert_methods:
        send_alert_slack(title=title, message=message)
    if "email" in alert_methods:
        send_email(
            subject=title,
            body=message,
        )

    return df
