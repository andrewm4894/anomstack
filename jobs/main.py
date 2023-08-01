"""
Main file for defining jobs and schedules.
"""

from jobs.ingest import ingest_jobs, ingest_schedules
from jobs.train import train_jobs, train_schedules
from jobs.score import score_jobs, score_schedules
from dagster import Definitions


# define job definitions
defs = Definitions(
    jobs=ingest_jobs + train_jobs + score_jobs,
    schedules=ingest_schedules + train_schedules + score_schedules,
)
