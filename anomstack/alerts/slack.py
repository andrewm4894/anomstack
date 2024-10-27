"""
Helper functions for sending alerts via Slack.

Slack alerts use a slack app. Below is a copy of the app manifest so you can
create your own. Instructions for creating a slack app from a manifest can
be found here: https://api.slack.com/reference/manifests#creating_apps

```json
{
    "display_information": {
        "name": "anomstack"
    },
    "features": {
        "bot_user": {
            "display_name": "anomstack",
            "always_online": false
        }
    },
    "oauth_config": {
        "redirect_urls": [
            "https://anomstack.com/"
        ],
        "scopes": {
            "bot": [
                "channels:read",
                "chat:write",
                "files:write",
                "groups:read"
            ]
        }
    },
    "settings": {
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```
"""

import os
import tempfile

import matplotlib.pyplot as plt
from dagster import get_dagster_logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from anomstack.plots.plot import make_alert_plot


def send_alert_slack(
    title="alert", message="hello", image_file_path=None, channel_name=None
) -> None:
    """
    Send alert via Slack API, optionally with an image.

    Args:
        title (str, optional): Title of the alert. Defaults to "alert".
        message (str, optional): Message of the alert. Defaults to "hello".
        image_file_path (str, optional): Path to image file to upload.
            Defaults to None.
        channel_name (str, optional): Slack channel name to send the message
            to. Defaults to None, in which case the environment variable
            'ANOMSTACK_SLACK_CHANNEL' is used.

    Returns:
        None
    """

    logger = get_dagster_logger()

    slack_token = os.environ.get("ANOMSTACK_SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError(
            (
                "Slack bot token not found in environment variable "
                "ANOMSTACK_SLACK_BOT_TOKEN"
            )
        )

    client = WebClient(token=slack_token)

    if not channel_name:
        channel_name = os.environ.get("ANOMSTACK_SLACK_CHANNEL")
        if not channel_name:
            raise ValueError(
                (
                    "Slack channel not specified in environment variable "
                    "'ANOMSTACK_SLACK_CHANNEL' or parameter channel_name"
                )
            )

    if channel_name.startswith("#"):
        channel_name = channel_name[1:]

    try:
        response = client.conversations_list(types="public_channel,private_channel")
        channels = response["channels"]
        channel_id = None
        for channel in channels:
            if channel["name"] == channel_name:
                channel_id = channel["id"]
                break
        if not channel_id:
            logger.error(f"Channel {channel_name} not found.")
            return
    except SlackApiError as e:
        logger.error(f"Error fetching channel ID: {e.response['error']}")
        return

    try:
        if image_file_path:
            with open(image_file_path, "rb") as file_content:
                response = client.files_upload_v2(
                    channels=[channel_id],
                    initial_comment=f"*{title}*\n{message}",
                    file=file_content,
                    filename=os.path.basename(image_file_path),
                )
        else:
            response = client.chat_postMessage(
                channel=channel_id, text=f"*{title}*\n{message}"
            )
        logger.debug(f"Slack response: {response}")
    except SlackApiError as e:
        logger.error(f"Error sending message to Slack: {e.response['error']}")


def send_alert_slack_with_plot(
    df,
    metric_name,
    title,
    message,
    threshold=0.8,
    score_col="metric_score_smooth",
    channel_name=None,
    metric_timestamp=None,
) -> None:
    """
    Sends an alert to Slack with a plot attached.
    """

    if not channel_name:
        channel_name = os.environ.get("ANOMSTACK_SLACK_CHANNEL")

    with tempfile.NamedTemporaryFile(
        prefix=f"{metric_name}_{metric_timestamp}_",
        suffix=".png",
        delete=False
    ) as temp:
        fig = make_alert_plot(df, metric_name, threshold, score_col)
        fig.savefig(temp.name)
        plt.close(fig)

        try:
            send_alert_slack(
                title=title,
                message=message,
                image_file_path=temp.name,
                channel_name=channel_name,
            )
        finally:
            os.unlink(temp.name)
