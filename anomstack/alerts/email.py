"""
Helper functions for sending alerts via email.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile
from anomstack.alerts.plot import make_plot


def send_email_with_plot(df, metric_name, subject, body, attachment_name) -> None:
    
    sender = os.getenv("ANOMSTACK_ALERT_EMAIL_FROM")
    password = os.getenv("ANOMSTACK_ALERT_EMAIL_PASSWORD")
    to = os.getenv("ANOMSTACK_ALERT_EMAIL_TO")
    host = os.getenv("ANOMSTACK_ALERT_EMAIL_SMTP_HOST")
    port = os.getenv("ANOMSTACK_ALERT_EMAIL_SMTP_PORT")

    with tempfile.NamedTemporaryFile(prefix=attachment_name, suffix=".png", delete=False) as temp:
        
        fig = make_plot(df, metric_name)
        fig.savefig(temp.name)

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = to
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        binary_file = open(temp.name, "rb")
        payload = MIMEBase('application', 'octate-stream', Name=f'{attachment_name}.png')
        payload.set_payload((binary_file).read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Decomposition', 'attachment', filename=f'{attachment_name}.png')
        msg.attach(payload)
        
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, to, text)
        server.quit()
        
        return None
