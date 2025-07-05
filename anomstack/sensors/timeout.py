"""Sensor to cancel long running Dagster runs."""

from __future__ import annotations

import os
import time
from typing import Optional

from dagster import (
    DagsterInstance,
    DagsterRunStatus,
    RunsFilter,
    SensorEvaluationContext,
    sensor,
)

MAX_RUNTIME_SECONDS = int(os.getenv("ANOMSTACK_RUN_TIMEOUT_SECONDS", "3600"))
CHECK_INTERVAL_SECONDS = int(os.getenv("ANOMSTACK_RUN_TIMEOUT_INTERVAL", "60"))


def terminate_long_running_runs(
    instance: Optional[DagsterInstance] = None,
    *,
    max_runtime: int = MAX_RUNTIME_SECONDS,
    log=None,
) -> None:
    """Cancel any runs executing longer than ``max_runtime`` seconds."""
    instance = instance or DagsterInstance.get()
    now = time.time()
    records = instance.get_run_records(
        RunsFilter(statuses=[DagsterRunStatus.STARTED, DagsterRunStatus.STARTING])
    )
    for record in records:
        if record.start_time and now - record.start_time > max_runtime:
            run_id = record.dagster_run.run_id
            if log:
                log.info(f"Canceling long running run {run_id}")
            if instance.run_coordinator:
                try:
                    instance.run_coordinator.cancel_run(run_id)
                except Exception as exc:  # pragma: no cover - best effort
                    if log:
                        log.warning(f"Failed to cancel run {run_id}: {exc}")
            else:
                instance.report_run_canceling(record.dagster_run)
                instance.run_launcher.terminate(run_id)
                instance.report_run_canceled(record.dagster_run)


@sensor(name="kill_long_running_runs", minimum_interval_seconds=CHECK_INTERVAL_SECONDS)
def kill_long_running_runs(context: SensorEvaluationContext):
    """Dagster sensor to cancel runs exceeding ``MAX_RUNTIME_SECONDS``."""
    terminate_long_running_runs(context.instance, log=context.log)
