"""Only the synthetic example jobs belong in the isolated local stack."""

from dagster import Definitions

from anomstack.main import jobs, schedules

# Production maintenance jobs use deployment paths, so don't register them locally.
defs = Definitions(
    jobs=[job for job in jobs if job.name.startswith("python_ingest_simple_")],
    schedules=[
        schedule for schedule in schedules if schedule.name.startswith("python_ingest_simple_")
    ],
)
