"""
Main file for defining jobs and schedules.
"""

from dagster import Definitions

from anomstack.jobs.alert import alert_jobs, alert_schedules
from anomstack.jobs.change import change_jobs, change_schedules
from anomstack.jobs.delete import delete_jobs, delete_schedules
from anomstack.jobs.ingest import ingest_jobs, ingest_schedules
from anomstack.jobs.llmalert import llmalert_jobs, llmalert_schedules
from anomstack.jobs.plot import plot_jobs, plot_schedules
from anomstack.jobs.score import score_jobs, score_schedules
from anomstack.jobs.summary import summary_jobs, summary_schedules
from anomstack.jobs.train import train_jobs, train_schedules
from anomstack.sensors.failure import email_on_run_failure
from anomstack.sensors.timeout import kill_long_running_runs

jobs = (
    ingest_jobs
    + train_jobs
    + score_jobs
    + alert_jobs
    + llmalert_jobs
    + plot_jobs
    + change_jobs
    + summary_jobs
    + delete_jobs
)
sensors = [email_on_run_failure, kill_long_running_runs]
schedules = (
    ingest_schedules
    + train_schedules
    + score_schedules
    + alert_schedules
    + llmalert_schedules
    + plot_schedules
    + change_schedules
    + summary_schedules
    + delete_schedules
)

defs = Definitions(
    jobs=jobs,
    schedules=schedules,
    sensors=sensors,
)
