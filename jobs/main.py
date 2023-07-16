from jobs.ingest import ingest_jobs, ingest_schedules
from jobs.train import train_jobs, train_schedules
from dagster import Definitions


defs = Definitions(
    jobs = ingest_jobs + train_jobs,
    schedules = ingest_schedules + train_schedules,
)