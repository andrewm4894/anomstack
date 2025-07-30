from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys

from dagster import DagsterInstance, DagsterRunStatus, RunsFilter

# Dynamically set DAGSTER_HOME to be parent of this script dir
script_dir = Path(__file__).resolve().parent
dagster_home = script_dir.parent.parent / "dagster_home"

os.environ["DAGSTER_HOME"] = str(dagster_home)
dagster_home.mkdir(parents=True, exist_ok=True)

# Set required Dagster environment variables
os.environ["ANOMSTACK_DAGSTER_SQLITE_STORAGE_BASE_DIR"] = "tmp"
os.environ["ANOMSTACK_DAGSTER_LOCAL_COMPUTE_LOG_MANAGER_DIRECTORY"] = "tmp"
os.environ["ANOMSTACK_DAGSTER_LOCAL_ARTIFACT_STORAGE_DIR"] = "tmp"

# Add the parent directory to sys.path to import the sensor module
sys.path.append(str(script_dir.parent.parent))
from anomstack.sensors.timeout import get_kill_after_minutes


def format_duration(duration):
    """Format duration in a readable way"""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def list_all_runs():
    """List all runs with their status and duration"""
    print("=" * 80)
    print("🔍 DAGSTER RUNS STATUS REPORT")
    print("=" * 80)

    instance = DagsterInstance.get()

    # Get all runs that aren't in a terminal state
    active_statuses = [
        DagsterRunStatus.STARTED,
        DagsterRunStatus.STARTING,
        DagsterRunStatus.QUEUED,
        DagsterRunStatus.CANCELING,
    ]

    active_runs = instance.get_runs(filters=RunsFilter(statuses=active_statuses))

    if not active_runs:
        print("✅ No active runs found!")
        return

    # Use the same configurable timeout as the sensor
    kill_after_minutes = get_kill_after_minutes()
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=kill_after_minutes)

    print(f"📋 Found {len(active_runs)} active runs")
    print(f"⏰ Timeout threshold: {kill_after_minutes} minutes")
    print("-" * 80)

    long_running_count = 0

    for i, run in enumerate(active_runs, 1):
        run_stats = instance.get_run_stats(run.run_id)

        # Get basic run info
        status_emoji = {
            DagsterRunStatus.STARTED: "🏃",
            DagsterRunStatus.STARTING: "🔄",
            DagsterRunStatus.QUEUED: "⏳",
            DagsterRunStatus.CANCELING: "🛑",
        }.get(run.status, "❓")

        print(f"\n{i}. {status_emoji} Run ID: {run.run_id[:12]}...")
        print(f"   Status: {run.status.value}")
        print(f"   Job: {run.job_name}")

        if run_stats.start_time is not None:
            started_at = datetime.fromtimestamp(run_stats.start_time, tz=timezone.utc)
            duration = datetime.now(timezone.utc) - started_at

            print(f"   Started: {started_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   Duration: {format_duration(duration)}")

            if started_at < cutoff_time:
                print(
                    f"   ⚠️  LONG RUNNING (>{kill_after_minutes}m) - Would be terminated by cleanup script"
                )
                long_running_count += 1
            else:
                print("   ✅ Within timeout threshold")
        else:
            print("   ⚠️  No start time available")

        # Add tags if any
        if run.tags:
            relevant_tags = {
                k: v
                for k, v in run.tags.items()
                if k in ["dagster/schedule_name", "dagster/sensor_name", "dagster/partition"]
            }
            if relevant_tags:
                print(f"   Tags: {relevant_tags}")

    print("-" * 80)
    print("📊 SUMMARY:")
    print(f"   Total active runs: {len(active_runs)}")
    print(f"   Long running (>{kill_after_minutes}m): {long_running_count}")

    if long_running_count > 0:
        print("\n💡 To terminate long running tasks, use:")
        print("   python scripts/maintenance/kill_long_running_tasks.py")

    print("=" * 80)


if __name__ == "__main__":
    try:
        list_all_runs()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
