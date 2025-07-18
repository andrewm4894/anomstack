import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from dagster import (
    DagsterRunStatus,
    RunsFilter,
    SensorEvaluationContext,
    SkipReason,
    sensor,
)
from dagster._core.errors import DagsterUserCodeUnreachableError

DEFAULT_MINUTES = 60

def _load_config_timeout_minutes() -> int:
    env_val = os.getenv("ANOMSTACK_KILL_RUN_AFTER_MINUTES")
    if env_val:
        try:
            return int(env_val)
        except ValueError:
            pass

    dagster_home = Path(os.getenv("DAGSTER_HOME", ""))
    if not dagster_home:
        dagster_home = Path.cwd()
    config_path = dagster_home / "dagster.yaml"
    minutes = DEFAULT_MINUTES
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            minutes = int(cfg.get("kill_sensor", {}).get("kill_after_minutes", minutes))
        except Exception:
            pass
    return minutes


def get_kill_after_minutes() -> int:
    """Return minutes after which to kill a running task."""
    return _load_config_timeout_minutes()


@sensor(minimum_interval_seconds=60)
def kill_long_running_runs(context: SensorEvaluationContext):
    """Terminate Dagster runs that exceed a configured runtime."""
    kill_after = get_kill_after_minutes()
    instance = context.instance
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=kill_after)
    running_runs = instance.get_runs(
        filters=RunsFilter(statuses=[DagsterRunStatus.STARTED])
    )
    killed = 0
    for run in running_runs:
        run_stats = instance.get_run_stats(run.run_id)
        if run_stats.start_time is None:
            continue
        started_at = datetime.fromtimestamp(run_stats.start_time, tz=timezone.utc)
        duration = datetime.now(timezone.utc) - started_at
        if started_at < cutoff:
            try:
                context.log.info(
                    f"Terminating run {run.run_id} running for {duration}"
                )
                instance.report_run_canceling(run)
                instance.run_launcher.terminate(run.run_id)
                killed += 1
            except DagsterUserCodeUnreachableError as exc:
                context.log.warning(
                    (
                        f"Could not terminate run {run.run_id}: {exc}. "
                        "Marking as failed."
                    )
                )
                instance.report_run_failed(run)
            except Exception as exc:
                context.log.error(
                    (
                        f"Unexpected error terminating run {run.run_id}: {exc}. "
                        "Marking as failed."
                    )
                )
                instance.report_run_failed(run)
    if killed == 0:
        yield SkipReason("No long running runs found")
    else:
        yield SkipReason(f"Killed {killed} long running run(s)")
