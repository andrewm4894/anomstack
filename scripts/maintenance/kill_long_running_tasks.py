from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys

from dagster import DagsterInstance, DagsterRunStatus, RunsFilter
from dagster._core.errors import DagsterUserCodeUnreachableError

# Dynamically set DAGSTER_HOME to be parent of this script dir
script_dir = Path(__file__).resolve().parent
dagster_home = script_dir.parent / ""

os.environ["DAGSTER_HOME"] = str(dagster_home)
dagster_home.mkdir(parents=True, exist_ok=True)

# Set required Dagster environment variables
os.environ["ANOMSTACK_DAGSTER_SQLITE_STORAGE_BASE_DIR"] = "tmp"
os.environ["ANOMSTACK_DAGSTER_LOCAL_COMPUTE_LOG_MANAGER_DIRECTORY"] = "tmp"
os.environ["ANOMSTACK_DAGSTER_LOCAL_ARTIFACT_STORAGE_DIR"] = "tmp"

# Add the parent directory to sys.path to import the sensor module
sys.path.append(str(script_dir.parent))
from anomstack.sensors.timeout import get_kill_after_minutes

# Use the same configurable timeout as the sensor
kill_after_minutes = get_kill_after_minutes()
cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=kill_after_minutes)
print(f"Using {kill_after_minutes} minute timeout")

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
                print(
                    f"Terminating run: {run.run_id} (started at {started_at}, duration {duration})"
                )
                instance.report_run_canceling(run)
                instance.run_launcher.terminate(run.run_id)
                print(f"✅ Successfully terminated run {run.run_id}")
            except DagsterUserCodeUnreachableError as e:
                print(f"⚠️ Could not terminate run {run.run_id}: {e}")
                print(
                    f"🔄 Marking run {run.run_id} as failed since user code server is unreachable"
                )
                # Mark the run as failed since we can't reach the user code server
                instance.report_run_failed(run)
                print(f"✅ Marked run {run.run_id} as failed")
            except Exception as e:
                print(f"⚠️ Unexpected error terminating run {run.run_id}: {e}")
                print(f"🔄 Marking run {run.run_id} as failed due to unexpected error")
                # Mark the run as failed for other errors too
                instance.report_run_failed(run)
                print(f"✅ Marked run {run.run_id} as failed")
        else:
            print(f"Skipping run {run.run_id} (only running for {duration})")
    else:
        print(f"Skipping run {run.run_id} (no start_time in stats)")
