import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

from dagster import DagsterInstance
from dagster._core.storage.pipeline_run import RunsFilter, DagsterRunStatus
from dagster import DagsterUserCodeExecutionError

# Dynamically set DAGSTER_HOME to be parent of this script dir
script_dir = Path(__file__).resolve().parent
dagster_home = script_dir.parent / ""

os.environ["DAGSTER_HOME"] = str(dagster_home)
dagster_home.mkdir(parents=True, exist_ok=True)

# Cutoff for long-running (1 hour ago)
cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)

instance = DagsterInstance.get()
running_runs = instance.get_runs(filters=RunsFilter(statuses=[DagsterRunStatus.STARTED]))

print(f"Found {len(running_runs)} running runs")

for run in running_runs:
    run_stats = instance.get_run_stats(run.run_id)

    if run_stats.start_time is not None:
        started_at = datetime.fromtimestamp(run_stats.start_time, tz=timezone.utc)
        duration = datetime.now(timezone.utc) - started_at

        if started_at < cutoff_time:
            try:
                print(f"Terminating run: {run.run_id} (started at {started_at}, duration {duration})")
                instance.report_run_canceling(run)
                instance.run_launcher.terminate(run.run_id)
            except DagsterUserCodeExecutionError as e:
                print(f"⚠️ Could not terminate run {run.run_id}: {e}")
        else:
            print(f"Skipping run {run.run_id} (only running for {duration})")
    else:
        print(f"Skipping run {run.run_id} (no start_time in stats)")
