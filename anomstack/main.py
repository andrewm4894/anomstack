"""
Main file for defining jobs and schedules.
"""

from anomstack.jobs.ingest import ingest_jobs, ingest_schedules
from anomstack.jobs.train import train_jobs, train_schedules
from anomstack.jobs.score import score_jobs, score_schedules
from anomstack.jobs.alert import alert_jobs, alert_schedules
from dagster import Definitions

jobs = ingest_jobs + train_jobs + score_jobs + alert_jobs

schedules = ingest_schedules + train_schedules + score_schedules + alert_schedules

defs = Definitions(
    jobs=jobs,
    schedules=schedules
)
