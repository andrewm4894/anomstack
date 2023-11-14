"""
Helper functions for sending alerts via email.
"""

import os
import smtplib
import ssl
import tempfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dagster import get_dagster_logger

from anomstack.plots.plot import make_alert_plot


def send_email_with_plot(
    df, metric_name, subject, body, attachment_name, threshold=0.8
) -> None:
    """
    Sends an email with a plot attached.

    Args:
        df (pandas.DataFrame): The dataframe containing the data to plot.
        metric_name (str): The name of the metric being plotted.
        subject (str): The subject of the email.
        body (str): The body of the email.
        attachment_name (str): The name of the attachment.
        threshold (float, optional): The threshold for the anomaly detection. Defaults to 0.8.

    Returns:
        None
    """

    logger = get_dagster_logger()

    sender = os.getenv("ANOMSTACK_ALERT_EMAIL_FROM")
    password = os.getenv("ANOMSTACK_ALERT_EMAIL_PASSWORD")
    to = os.getenv("ANOMSTACK_ALERT_EMAIL_TO")
    host = os.getenv("ANOMSTACK_ALERT_EMAIL_SMTP_HOST")
    port = os.getenv("ANOMSTACK_ALERT_EMAIL_SMTP_PORT")

    with tempfile.NamedTemporaryFile(
        prefix=attachment_name, suffix=".png", delete=False
    ) as temp:
        fig = make_alert_plot(df, metric_name, threshold)
        fig.savefig(temp.name)

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))
        binary_file = open(temp.name, "rb")
        payload = MIMEBase(
            "application", "octate-stream", Name=f"{attachment_name}.png"
        )
        payload.set_payload((binary_file).read())
        encoders.encode_base64(payload)
        payload.add_header(
            "Content-Decomposition", "attachment", filename=f"{attachment_name}.png"
        )
        msg.attach(payload)

        context = ssl.create_default_context()
        with smtplib.SMTP(host, port) as server:
            server.connect(host, port)
            server.starttls(context=context)
            server.login(sender, password)
            text = msg.as_string()
            server.sendmail(sender, to, text)
            server.quit()

    logger.info(f"email '{subject}' sent to {to}")
