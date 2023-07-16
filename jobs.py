from ingest_jobs import ingest_jobs, ingest_schedules
from train_jobs import train_jobs, train_schedules
from dagster import Definitions


defs = Definitions(
    jobs = ingest_jobs + train_jobs,
    schedules = ingest_schedules + train_schedules,
)