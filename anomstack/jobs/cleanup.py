"""
Cleanup job for managing disk space and removing old artifacts.
"""

from datetime import datetime, timedelta
import os
import shutil
import sqlite3

from dagster import (
    DefaultScheduleStatus,
    ScheduleDefinition,
    get_dagster_logger,
    job,
    op,
)


@op
def cleanup_old_artifacts():
    """Clean up old Dagster artifacts to free disk space."""
    logger = get_dagster_logger()

    artifacts_path = "/data/artifacts/storage"
    if not os.path.exists(artifacts_path):
        logger.info("Artifacts directory does not exist, skipping cleanup")
        return

    # Remove artifacts older than 6 hours
    cutoff_time = datetime.now() - timedelta(hours=6)
    removed_count = 0
    freed_bytes = 0

    try:
        for item in os.listdir(artifacts_path):
            item_path = os.path.join(artifacts_path, item)
            if os.path.isdir(item_path):
                # Get directory modification time
                mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                if mod_time < cutoff_time:
                    # Calculate size before removal
                    try:
                        size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(item_path)
                            for filename in filenames
                        )
                        shutil.rmtree(item_path)
                        removed_count += 1
                        freed_bytes += size
                        logger.info(f"Removed old artifact directory: {item}")
                    except Exception as e:
                        logger.warning(f"Failed to remove {item_path}: {e}")

        freed_mb = freed_bytes / (1024 * 1024)
        logger.info(
            f"Cleanup complete: removed {removed_count} directories, freed {freed_mb:.1f}MB"
        )

    except Exception as e:
        logger.error(f"Error during artifact cleanup: {e}")


@op
def cleanup_old_logs():
    """Clean up old log files."""
    logger = get_dagster_logger()

    log_dirs = ["/tmp/dagster", "/data/dagster_storage"]
    removed_count = 0
    freed_bytes = 0

    for log_dir in log_dirs:
        if not os.path.exists(log_dir):
            continue

        try:
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    if file.endswith((".log", ".out", ".err")):
                        file_path = os.path.join(root, file)
                        # Remove log files older than 24 hours
                        if (
                            os.path.getmtime(file_path)
                            < (datetime.now() - timedelta(hours=24)).timestamp()
                        ):
                            try:
                                size = os.path.getsize(file_path)
                                os.remove(file_path)
                                removed_count += 1
                                freed_bytes += size
                            except Exception as e:
                                logger.warning(f"Failed to remove log file {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error cleaning logs in {log_dir}: {e}")

    freed_mb = freed_bytes / (1024 * 1024)
    logger.info(f"Log cleanup complete: removed {removed_count} files, freed {freed_mb:.1f}MB")


@op
def cleanup_old_metrics():
    """Clean up old metric data from database."""
    logger = get_dagster_logger()

    db_path = "/data/anomstack.db"
    if not os.path.exists(db_path):
        logger.info("Database does not exist, skipping metric cleanup")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Remove metrics older than 90 days
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # Get count before deletion
        cursor.execute("SELECT COUNT(*) FROM metrics WHERE metric_timestamp < ?", (cutoff_date,))
        old_count = cursor.fetchone()[0]

        # Delete old metrics
        cursor.execute("DELETE FROM metrics WHERE metric_timestamp < ?", (cutoff_date,))

        # Vacuum to reclaim space
        cursor.execute("VACUUM")

        conn.commit()
        conn.close()

        logger.info(f"Database cleanup complete: removed {old_count} old metric records")

    except Exception as e:
        logger.error(f"Error during database cleanup: {e}")


@op
def report_disk_usage():
    """Report current disk usage."""
    logger = get_dagster_logger()

    try:
        # Get disk usage for /data
        statvfs = os.statvfs("/data")
        total_bytes = statvfs.f_frsize * statvfs.f_blocks
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        used_bytes = total_bytes - free_bytes

        total_gb = total_bytes / (1024**3)
        used_gb = used_bytes / (1024**3)
        free_gb = free_bytes / (1024**3)
        usage_percent = (used_bytes / total_bytes) * 100

        logger.info(
            f"Disk usage - Total: {total_gb:.1f}GB, Used: {used_gb:.1f}GB ({usage_percent:.1f}%), Free: {free_gb:.1f}GB"
        )

        # Get directory sizes
        data_dirs = ["/data/artifacts", "/data/dagster_storage", "/data/models"]
        for dir_path in data_dirs:
            if os.path.exists(dir_path):
                try:
                    total_size = sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(dir_path)
                        for filename in filenames
                    )
                    size_gb = total_size / (1024**3)
                    logger.info(f"{dir_path}: {size_gb:.2f}GB")
                except Exception as e:
                    logger.warning(f"Could not calculate size for {dir_path}: {e}")

    except Exception as e:
        logger.error(f"Error reporting disk usage: {e}")


@job(
    name="cleanup_disk_space",
    description="Clean up old artifacts, logs, and metrics to free disk space",
)
def cleanup_job():
    """Job to clean up disk space."""
    report_disk_usage()
    cleanup_old_artifacts()
    cleanup_old_logs()
    cleanup_old_metrics()
    report_disk_usage()  # Report again after cleanup


# Create schedule to run cleanup every 2 hours
cleanup_schedule = ScheduleDefinition(
    job=cleanup_job,
    cron_schedule="0 */2 * * *",  # Every 2 hours
    default_status=DefaultScheduleStatus.RUNNING,
)

# Export for main.py
cleanup_jobs = [cleanup_job]
cleanup_schedules = [cleanup_schedule]
