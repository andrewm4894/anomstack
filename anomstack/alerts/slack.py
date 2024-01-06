"""
Helper functions for sending alerts via Slack.
"""

import json
import os

import requests
from dagster import get_dagster_logger


def send_alert_slack(
    title="alert", message="hello", env_var_webhook_url="ANOMSTACK_SLACK_WEBHOOK_URL"
) -> requests.Response:
    """
    Send alert via webhook.

    Args:
        title (str, optional): Title of the alert. Defaults to "alert".
        message (str, optional): Message of the alert. Defaults to "hello".
        env_var_webhook_url (str, optional): Environment variable name for the webhook URL. Defaults to "ANOMSTACK_SLACK_WEBHOOK_URL".

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
