from jobs.ingest import ingest_jobs, ingest_schedules
from jobs.models import models
from jobs.score import score_jobs, score_schedules
from dagster import Definitions


defs = Definitions(
    jobs = ingest_jobs + score_jobs,
    schedules = ingest_schedules + score_schedules,
    assets=models
)