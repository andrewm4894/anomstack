"""
Helper functions for sending alerts via Slack.
"""

import json
import os
import tempfile
from dagster import get_dagster_logger
from anomstack.plots.plot import make_alert_plot

import requests
from dagster import get_dagster_logger


def send_alert_slack(
    title="alert",
    message="hello",
    env_var_webhook_url="ANOMSTACK_SLACK_WEBHOOK_URL"
) -> requests.Response:
    """
    Send alert via webhook.

    Args:
        title (str, optional): Title of the alert. Defaults to "alert".
        message (str, optional): Message of the alert. Defaults to "hello".
        env_var_webhook_url (str, optional): Environment variable name for the
            webhook URL. Defaults to "ANOMSTACK_SLACK_WEBHOOK_URL".

    Returns:
        requests.Response: Response from the Slack API.
    """

    logger = get_dagster_logger()

    webhook_url = os.environ[env_var_webhook_url]
    payload = {
        #'text': f'{title}',
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": title}},
            {"type": "section", "text": {"type": "mrkdwn", "text": message}},
        ]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        webhook_url, data=json.dumps(payload), headers=headers, timeout=10
    )

    logger.debug(f"slack response: {response}")

    return response


def send_alert_slack_with_plot(
    df,
    metric_name,
    title="alert",
    message="hello",
    env_var_webhook_url="ANOMSTACK_SLACK_WEBHOOK_URL",
    threshold=0.8,
    score_col="metric_score_smooth"
) -> requests.Response:
    """
    Send an alert via Slack with a plot image.

    Args:
        df (pandas.DataFrame): The dataframe containing the data to plot.
        metric_name (str): The name of the metric being plotted.
        title (str, optional): Title of the alert. Defaults to "alert".
        message (str, optional): Message of the alert. Defaults to "hello".
        env_var_webhook_url (str, optional): Environment variable name for the
            webhook URL. Defaults to "ANOMSTACK_SLACK_WEBHOOK_URL".
        threshold (float, optional): The threshold for anomaly detection. Defaults to 0.8.
        score_col (str, optional): The column containing anomaly scores. Defaults to "metric_score_smooth".

    Returns:
        requests.Response: Response from the Slack API.
    """

    logger = get_dagster_logger()

    # Slack Webhook and Token for file upload
    webhook_url = os.environ[env_var_webhook_url]
    slack_token = os.environ["ANOMSTACK_SLACK_BOT_TOKEN"]

    # Step 1: Generate plot and save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        fig = make_alert_plot(df, metric_name, threshold, score_col)
        fig.savefig(temp.name)
        temp_path = temp.name

    # Step 2: Upload the file to Slack and retrieve file ID
    with open(temp_path, "rb") as file:
        response = requests.post(
            "https://slack.com/api/files.upload",
            headers={"Authorization": f"Bearer {slack_token}"},
            data={"channels": "#dev-bot"},  # Specify the channel name or ID
            files={"file": file},
        )

    file_upload_data = response.json()
    if not file_upload_data.get("ok"):
        logger.error("Failed to upload image to Slack.")
        return response

    # Retrieve the file ID from the upload response
    file_id = file_upload_data["file"]["id"]

    # Step 3: Construct the alert message with an image reference
    payload = {
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*\n{message}"}},
            {"type": "image", "image_url": file_upload_data["file"]["url_private"], "alt_text": "Alert plot"},
        ]
    }

    # Step 4: Send alert message to Slack
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {slack_token}",
    }
    response = requests.post(
        webhook_url, 
        data=json.dumps(payload), 
        headers=headers, 
        timeout=10
    )

    logger.debug(f"Slack response: {response}")
    return response


def bot_send_slack_alert_with_file(
    df,
    metric_name,
    title="alert",
    message="hello",
    threshold=0.8,
    score_col="metric_score_smooth",
    channel="#dev-bot"
):
    """
    Sends an alert with a plot to Slack using bot token authentication.

    Args:
        df (pandas.DataFrame): Data for plotting.
        metric_name (str): Name of the metric being plotted.
        title (str): Title of the alert.
        message (str): Alert message.
        threshold (float): Threshold for plotting.
        score_col (str): Column name for scores.
        channel (str): Slack channel to send the alert.

    Returns:
        requests.Response: Response from Slack API.
    """

    logger = get_dagster_logger()
    slack_token = os.getenv("ANOMSTACK_SLACK_BOT_TOKEN")

    # Step 1: Generate and save the plot as a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        fig = make_alert_plot(df, metric_name, threshold, score_col)
        fig.savefig(temp.name)
        temp_path = temp.name

    # Step 2: Upload the file to Slack and get the private URL
    with open(temp_path, "rb") as file:
        upload_response = requests.post(
            "https://slack.com/api/files.upload",
            headers={"Authorization": f"Bearer {slack_token}"},
            data={"channels": channel},
            files={"file": file}
        )

    upload_data = upload_response.json()
    if not upload_data.get("ok"):
        logger.error("Failed to upload image to Slack.")
        return upload_response

    # Retrieve the file's URL for the uploaded image
    file_url = upload_data["file"]["url_private"]

    # Step 3: Send the alert message with the image link
    alert_payload = {
        "channel": channel,
        "text": f"*{title}*\n{message}",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*\n{message}"}},
            {"type": "image", "image_url": file_url, "alt_text": "Alert plot"}
        ]
    }

    message_response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {slack_token}"
        },
        data=json.dumps(alert_payload)
    )

    logger.debug(f"Slack message response: {message_response}")
    return message_response
