import logging

import pytest

from anomstack.main import ingest_jobs, ingest_schedules, jobs, schedules

logger = logging.getLogger(__name__)


def test_jobs_len():
    assert len(jobs) == 126


def test_jobs_len_ingest():
    assert len(ingest_jobs) == len(jobs) / 7


def test_schedules_len():
    assert len(schedules) == 126


def test_schedules_len_ingest():
    assert len(ingest_schedules) == len(schedules) / 7


def test_jobs_schedules_len_match():
    assert len(jobs) == len(schedules)


# Run the test
pytest.main()
