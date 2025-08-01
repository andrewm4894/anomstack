import logging

import pytest

# Now we can import the modules
from anomstack.main import ingest_jobs, ingest_schedules, jobs, schedules

logger = logging.getLogger(__name__)


def test_jobs_len():
    assert len(jobs) == 209  # Updated for new example metric batches


def test_jobs_len_ingest():
    assert len(ingest_jobs) == (len(jobs) - 1) / 8  # Back to original (cleanup job disabled)


def test_schedules_len():
    assert len(schedules) == 209  # Updated for new example metric batches


def test_schedules_len_ingest():
    assert (
        len(ingest_schedules) == (len(schedules) - 1) / 8
    )  # Back to original (cleanup schedule disabled)


def test_jobs_schedules_len_match():
    assert len(jobs) == len(schedules)


def test_main_imports():
    """Test that the main module imports work correctly."""
    assert len(jobs) > 0
    assert len(schedules) > 0


# Run the test
pytest.main()
