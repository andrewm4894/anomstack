"""
Main file for defining jobs and schedules.
"""

from dagster import Definitions
from anomstack.jobs.ingest import ingest_jobs, ingest_schedules
from anomstack.jobs.train import train_jobs, train_schedules
from anomstack.jobs.score import score_jobs, score_schedules
from anomstack.jobs.alert import alert_jobs, alert_schedules
from anomstack.jobs.llmalert import llmalert_jobs, llmalert_schedules
from anomstack.jobs.timegptalert import timegptalert_jobs, timegptalert_schedules
from anomstack.jobs.plot import plot_jobs, plot_schedules
from anomstack.sensors.failure import email_on_run_failure


jobs = (
    ingest_jobs
    + train_jobs
    + score_jobs
    + alert_jobs
    + llmalert_jobs
    + timegptalert_jobs
    + plot_jobs
)
schedules = (
    ingest_schedules
    + train_schedules
    + score_schedules
    + alert_schedules
    + llmalert_schedules
    + timegptalert_schedules
    + plot_schedules
)
sensors = [email_on_run_failure]

defs = Definitions(
    jobs=jobs,
    schedules=schedules,
    sensors=sensors,
)
