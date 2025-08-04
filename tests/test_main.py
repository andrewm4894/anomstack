import logging

import pytest

# Now we can import the modules
from anomstack.main import ingest_jobs, ingest_schedules, jobs, schedules

logger = logging.getLogger(__name__)


def test_jobs_len():
    assert len(jobs) == 203  # Updated for current example metric batches


def test_jobs_len_ingest():
    assert len(ingest_jobs) == 25  # 25 ingest jobs in current setup


def test_schedules_len():
    assert len(schedules) == 203  # Updated for current example metric batches


def test_schedules_len_ingest():
    assert len(ingest_schedules) == 25  # 25 ingest schedules in current setup


def test_jobs_schedules_len_match():
    assert len(jobs) == len(schedules)


def test_main_imports():
    """Test that the main module imports work correctly."""
    assert len(jobs) > 0
    assert len(schedules) > 0


# Run the test
pytest.main()
