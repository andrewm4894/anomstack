"""
Main file for defining jobs and schedules.
"""

import os
from anomstack.jobs.ingest import ingest_jobs, ingest_schedules
from anomstack.jobs.train import train_jobs, train_schedules
from anomstack.jobs.score import score_jobs, score_schedules
from anomstack.jobs.alert import alert_jobs, alert_schedules
from dagster import Definitions
from dagster import make_email_on_run_failure_sensor


email_on_run_failure = make_email_on_run_failure_sensor(
    email_from=os.getenv("ANOMSTACK_ALERT_EMAIL_FROM"),
    email_password=os.getenv("ANOMSTACK_ALERT_EMAIL_PASSWORD"),
    email_to=os.getenv("ANOMSTACK_ALERT_EMAIL_TO").split(","),
)

jobs = ingest_jobs + train_jobs + score_jobs + alert_jobs
sensors = [email_on_run_failure]
schedules = ingest_schedules + train_schedules + score_schedules + alert_schedules

defs = Definitions(
    jobs=jobs,
    schedules=schedules,
    sensors=sensors,
)
