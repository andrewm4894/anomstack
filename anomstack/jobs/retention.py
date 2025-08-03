"""
Custom retention job since Dagster SQLite doesn't support built-in retention.
Configurable via environment variables with sensible defaults.

Environment Variables:
    ANOMSTACK_RETENTION_DAYS (default: "1")
        Number of days to keep Dagster runs. Runs older than this will be purged.

    ANOMSTACK_RETENTION_SCHEDULE (default: "0 */6 * * *")
        Cron expression for when retention job runs. Default is every 6 hours.

    ANOMSTACK_RETENTION_ENABLED (default: "true")
        Whether retention is enabled. Set to "false" to disable completely.

    ANOMSTACK_RETENTION_VACUUM (default: "true")
        Whether to vacuum the SQLite database after deletions to reclaim space.

    ANOMSTACK_RETENTION_BATCH_SIZE (default: "1000")
        Number of runs to delete per batch. Helps with memory usage for large datasets.

    ANOMSTACK_DAGSTER_STORAGE_PATH (default: "/data/dagster_storage")
        Base path to Dagster storage directory.

Examples:
    # Keep runs for 3 days instead of 1
    export ANOMSTACK_RETENTION_DAYS=3

    # Run retention daily at midnight instead of every 6 hours
    export ANOMSTACK_RETENTION_SCHEDULE="0 0 * * *"

    # Disable retention completely
    export ANOMSTACK_RETENTION_ENABLED=false

    # Use different storage path (for development)
    export ANOMSTACK_DAGSTER_STORAGE_PATH=/tmp/dagster_storage
"""

from datetime import datetime, timedelta
import os
import sqlite3

from dagster import (
    DefaultScheduleStatus,
    ScheduleDefinition,
    get_dagster_logger,
    job,
    op,
)

# Configuration from environment variables with sensible defaults
RETENTION_DAYS = int(os.getenv("ANOMSTACK_RETENTION_DAYS", "1"))  # Days to keep runs
RETENTION_SCHEDULE = os.getenv("ANOMSTACK_RETENTION_SCHEDULE", "0 */6 * * *")  # Every 6 hours
RETENTION_ENABLED = os.getenv("ANOMSTACK_RETENTION_ENABLED", "true").lower() == "true"
RETENTION_VACUUM = os.getenv("ANOMSTACK_RETENTION_VACUUM", "true").lower() == "true"
RETENTION_BATCH_SIZE = int(os.getenv("ANOMSTACK_RETENTION_BATCH_SIZE", "1000"))  # Delete in batches
DAGSTER_STORAGE_PATH = os.getenv("ANOMSTACK_DAGSTER_STORAGE_PATH", "/data/dagster_storage")


@op
def purge_old_runs():
    """Manually purge old runs from SQLite storage."""
    logger = get_dagster_logger()

    if not RETENTION_ENABLED:
        logger.info("Retention is disabled via ANOMSTACK_RETENTION_ENABLED")
        return

    db_path = f"{DAGSTER_STORAGE_PATH}/history/runs.db"
    if not os.path.exists(db_path):
        logger.info(f"Runs database not found at {db_path}")
        return

    # Delete runs older than configured days
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    cutoff_timestamp = cutoff.timestamp()

    logger.info(f"Purging runs older than {RETENTION_DAYS} days (before {cutoff.isoformat()})")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get count before deletion
        cursor.execute("SELECT COUNT(*) FROM runs WHERE create_timestamp < ?", (cutoff_timestamp,))
        old_count = cursor.fetchone()[0]

        if old_count > 0:
            logger.info(f"Found {old_count} runs to purge")

            # Delete in batches to avoid memory issues with large datasets
            total_deleted = 0
            while True:
                cursor.execute(
                    "DELETE FROM runs WHERE run_id IN ("
                    "SELECT run_id FROM runs WHERE create_timestamp < ? LIMIT ?"
                    ")",
                    (cutoff_timestamp, RETENTION_BATCH_SIZE),
                )
                batch_deleted = cursor.rowcount
                if batch_deleted == 0:
                    break

                total_deleted += batch_deleted
                conn.commit()
                logger.info(f"Deleted batch of {batch_deleted} runs (total: {total_deleted})")

                # Small delay between batches
                if total_deleted < old_count:
                    import time

                    time.sleep(0.1)

            logger.info(f"Purged {total_deleted} runs older than {RETENTION_DAYS} days")

            # Clean up orphaned run files in the filesystem
            runs_dir = f"{DAGSTER_STORAGE_PATH}/history/runs"
            if os.path.exists(runs_dir):
                cleaned_files = 0
                for filename in os.listdir(runs_dir):
                    if filename.endswith(".db"):
                        file_path = os.path.join(runs_dir, filename)
                        try:
                            # Check if this run_id still exists in the database
                            run_id = filename.replace(".db", "")
                            cursor.execute("SELECT COUNT(*) FROM runs WHERE run_id = ?", (run_id,))
                            if cursor.fetchone()[0] == 0:
                                os.remove(file_path)
                                cleaned_files += 1
                        except Exception as e:
                            logger.warning(f"Failed to clean up run file {filename}: {e}")

                if cleaned_files > 0:
                    logger.info(f"Cleaned up {cleaned_files} orphaned run files")

            # Vacuum to reclaim space (optional)
            if RETENTION_VACUUM:
                logger.info("Vacuuming database to reclaim space...")
                cursor.execute("VACUUM")
                logger.info("Database vacuum completed")
        else:
            logger.info("No old runs to purge")

        # Report current run count and database size
        cursor.execute("SELECT COUNT(*) FROM runs")
        current_count = cursor.fetchone()[0]

        # Get database file size
        db_size_mb = os.path.getsize(db_path) / (1024 * 1024)

        logger.info(f"Current total runs: {current_count}, database size: {db_size_mb:.1f}MB")

        conn.close()

    except Exception as e:
        logger.error(f"Error purging runs: {e}")
        raise


@op
def purge_old_run_files():
    """Clean up old run files from filesystem that might not be in database."""
    logger = get_dagster_logger()

    if not RETENTION_ENABLED:
        logger.info("Retention is disabled via ANOMSTACK_RETENTION_ENABLED")
        return

    runs_dir = f"{DAGSTER_STORAGE_PATH}/history/runs"
    if not os.path.exists(runs_dir):
        logger.info(f"Runs directory not found at {runs_dir}")
        return

    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    cleaned_files = 0
    freed_bytes = 0

    logger.info(f"Cleaning run files older than {RETENTION_DAYS} days")

    try:
        for filename in os.listdir(runs_dir):
            if filename.endswith(".db"):
                file_path = os.path.join(runs_dir, filename)
                try:
                    # Check file modification time
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mod_time < cutoff:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleaned_files += 1
                        freed_bytes += file_size
                except Exception as e:
                    logger.warning(f"Failed to process run file {filename}: {e}")

        if cleaned_files > 0:
            freed_mb = freed_bytes / (1024 * 1024)
            logger.info(f"Cleaned up {cleaned_files} old run files, freed {freed_mb:.1f}MB")
        else:
            logger.info("No old run files to clean up")

    except Exception as e:
        logger.error(f"Error cleaning run files: {e}")


@op
def report_retention_config():
    """Log the current retention configuration."""
    logger = get_dagster_logger()

    logger.info("=== Retention Configuration ===")
    logger.info(f"Enabled: {RETENTION_ENABLED}")
    logger.info(f"Retention period: {RETENTION_DAYS} days")
    logger.info(f"Schedule: {RETENTION_SCHEDULE}")
    logger.info(f"Vacuum database: {RETENTION_VACUUM}")
    logger.info(f"Batch size: {RETENTION_BATCH_SIZE}")
    logger.info(f"Storage path: {DAGSTER_STORAGE_PATH}")
    logger.info("===============================")


@job(name="retention_cleanup")
def retention_job():
    """Job to clean up old Dagster runs and run files."""
    report_retention_config()
    purge_old_runs()
    purge_old_run_files()


# Create schedule with configurable cron expression
retention_schedule = ScheduleDefinition(
    job=retention_job,
    cron_schedule=RETENTION_SCHEDULE,
    default_status=DefaultScheduleStatus.RUNNING
    if RETENTION_ENABLED
    else DefaultScheduleStatus.STOPPED,
)

# Export for main.py
retention_jobs = [retention_job]
retention_schedules = [retention_schedule]
