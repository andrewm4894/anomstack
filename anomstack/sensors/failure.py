import os

from dagster import make_email_on_run_failure_sensor
from dotenv import load_dotenv

load_dotenv()

email_from = os.getenv(
    "ANOMSTACK_FAILURE_EMAIL_FROM", os.getenv("ANOMSTACK_ALERT_EMAIL_FROM")
)
email_password = os.getenv(
    "ANOMSTACK_FAILURE_EMAIL_PASSWORD", os.getenv("ANOMSTACK_ALERT_EMAIL_PASSWORD")
)
email_to = os.getenv(
    "ANOMSTACK_FAILURE_EMAIL_TO", os.getenv("ANOMSTACK_ALERT_EMAIL_TO")
).split(",")

email_on_run_failure = make_email_on_run_failure_sensor(
    email_from=email_from,
    email_password=email_password,
    email_to=email_to,
    monitor_all_repositories=True,
)
