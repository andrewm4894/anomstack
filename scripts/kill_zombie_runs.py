"""Utility script to cancel long running Dagster runs."""

from anomstack.sensors.timeout import terminate_long_running_runs

if __name__ == "__main__":
    terminate_long_running_runs()
