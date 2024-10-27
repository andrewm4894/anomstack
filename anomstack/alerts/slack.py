"""
Helper functions for sending alerts via Slack.
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dagster import get_dagster_logger
import matplotlib.pyplot as plt
import tempfile
from anomstack.plots.plot import make_alert_plot


def send_alert_slack(
    title="alert",
    message="hello",
    image_file_path=None,
    env_var_bot_token="ANOMSTACK_SLACK_BOT_TOKEN",
    channel_name=None
) -> None:
    """
    Send alert via Slack API, optionally with an image.

    Args:
        title (str, optional): Title of the alert. Defaults to "alert".
        message (str, optional): Message of the alert. Defaults to "hello".
        image_file_path (str, optional): Path to image file to upload. Defaults to None.
        env_var_bot_token (str, optional): Environment variable name for the bot token.
            Defaults to "ANOMSTACK_SLACK_BOT_TOKEN".
        channel_name (str, optional): Slack channel name to send the message to.
            Defaults to None, in which case the environment variable 'ANOMSTACK_SLACK_CHANNEL' is used.

    Returns:
        None
    """

    logger = get_dagster_logger()

    slack_token = os.environ.get(env_var_bot_token)
    if not slack_token:
        raise ValueError(f"Slack bot token not found in environment variable {env_var_bot_token}")

    client = WebClient(token=slack_token)

    if not channel_name:
        channel_name = os.environ.get('ANOMSTACK_SLACK_CHANNEL')
        if not channel_name:
            raise ValueError(
                "Slack channel not specified in environment variable 'ANOMSTACK_SLACK_CHANNEL' or parameter channel_name"
            )

    # Remove leading '#' if present
    if channel_name.startswith('#'):
        channel_name = channel_name[1:]

    # Get the channel ID
    try:
        response = client.conversations_list(types='public_channel,private_channel')
        channels = response['channels']
        channel_id = None
        for channel in channels:
            if channel['name'] == channel_name:
                channel_id = channel['id']
                break
        if not channel_id:
            logger.error(f"Channel {channel_name} not found.")
            return
    except SlackApiError as e:
        logger.error(f"Error fetching channel ID: {e.response['error']}")
        return

    try:
        # Send message with or without image
        if image_file_path:
            # Upload the image
            with open(image_file_path, 'rb') as file_content:
                response = client.files_upload_v2(
                    channels=[channel_id],
                    initial_comment=f"*{title}*\n{message}",
                    file=file_content,
                    filename=os.path.basename(image_file_path)
                )
        else:
            # Send message without image
            response = client.chat_postMessage(
                channel=channel_id,
                text=f"*{title}*\n{message}"
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
    env_var_bot_token="ANOMSTACK_SLACK_BOT_TOKEN",
    channel_name=None
) -> None:
    """
    Sends an alert to Slack with a plot attached.
    """
    logger = get_dagster_logger()

    # Generate the plot and save to temporary file
    with tempfile.NamedTemporaryFile(prefix=metric_name, suffix=".png", delete=False) as temp:
        fig = make_alert_plot(df, metric_name, threshold, score_col)
        fig.savefig(temp.name)
        plt.close(fig)  # Properly close the figure

        # Send the alert to Slack
        try:
            send_alert_slack(
                title=title,
                message=message,
                image_file_path=temp.name,
                env_var_bot_token=env_var_bot_token,
                channel_name=channel_name
            )
        finally:
            # Clean up the temp file
            os.unlink(temp.name)
