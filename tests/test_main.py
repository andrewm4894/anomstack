import pytest
import logging
from anomstack.main import (
    jobs,
    schedules,
    ingest_jobs,
    ingest_schedules,
)

logger = logging.getLogger(__name__)


def test_jobs_len():
    assert len(jobs) == 102


def test_jobs_len_ingest():
    assert len(ingest_jobs) == len(jobs) / 6


def test_schedules_len():
    assert len(schedules) == 102


def test_schedules_len_ingest():
    assert len(ingest_schedules) == len(schedules) / 6


def test_jobs_schedules_len_match():
    assert len(jobs) == len(schedules)


# Run the test
pytest.main()
