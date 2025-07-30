#!/usr/bin/env python3
"""
Standalone script for cleaning up disk space on Fly.io instances.
Can be run manually or via cron for emergency cleanup.

Usage:
    python cleanup_disk_space.py [--dry-run] [--aggressive] [--help]

Options:
    --dry-run     Show what would be deleted without actually deleting
    --aggressive  Use more aggressive cleanup (1 hour for artifacts, remove all logs)
    --help        Show this help message
"""

import argparse
from datetime import datetime, timedelta
import os
import shutil
import sqlite3


def get_disk_usage(path="/data"):
    """Get disk usage statistics."""
    try:
        statvfs = os.statvfs(path)
        total_bytes = statvfs.f_frsize * statvfs.f_blocks
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        used_bytes = total_bytes - free_bytes

        return {
            "total_gb": total_bytes / (1024**3),
            "used_gb": used_bytes / (1024**3),
            "free_gb": free_bytes / (1024**3),
            "usage_percent": (used_bytes / total_bytes) * 100,
        }
    except Exception as e:
        print(f"Error getting disk usage: {e}")
        return None


def cleanup_artifacts(dry_run=False, aggressive=False):
    """Clean up old Dagster artifacts."""
    artifacts_path = "/data/artifacts/storage"
    if not os.path.exists(artifacts_path):
        print("❌ Artifacts directory does not exist")
        return 0, 0

    # Normal: 6 hours, Aggressive: 1 hour
    hours_back = 1 if aggressive else 6
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    print(f"🧹 Cleaning artifacts older than {hours_back} hours...")

    removed_count = 0
    freed_bytes = 0

    try:
        items = os.listdir(artifacts_path)
        print(f"Found {len(items)} artifact directories")

        for item in items:
            item_path = os.path.join(artifacts_path, item)
            if os.path.isdir(item_path):
                mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                if mod_time < cutoff_time:
                    # Calculate size
                    try:
                        size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(item_path)
                            for filename in filenames
                        )

                        if dry_run:
                            print(f"Would remove: {item} ({size/(1024**2):.1f}MB)")
                        else:
                            shutil.rmtree(item_path)
                            print(f"Removed: {item} ({size/(1024**2):.1f}MB)")

                        removed_count += 1
                        freed_bytes += size

                    except Exception as e:
                        print(f"⚠️  Failed to process {item}: {e}")

        action = "Would free" if dry_run else "Freed"
        print(f"✅ {action} {freed_bytes/(1024**2):.1f}MB by removing {removed_count} directories")

    except Exception as e:
        print(f"❌ Error during artifact cleanup: {e}")

    return removed_count, freed_bytes


def cleanup_logs(dry_run=False, aggressive=False):
    """Clean up old log files."""
    log_dirs = ["/tmp/dagster", "/data/dagster_storage", "/tmp"]

    # Normal: 24 hours, Aggressive: remove all logs
    if aggressive:
        print("🧹 Removing ALL log files (aggressive mode)...")
        cutoff_time = datetime.now()  # Remove all logs
    else:
        print("🧹 Removing log files older than 24 hours...")
        cutoff_time = datetime.now() - timedelta(hours=24)

    removed_count = 0
    freed_bytes = 0

    for log_dir in log_dirs:
        if not os.path.exists(log_dir):
            continue

        print(f"Checking {log_dir}...")

        try:
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    if file.endswith((".log", ".out", ".err")) or "dagster" in file.lower():
                        file_path = os.path.join(root, file)
                        try:
                            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            if file_time < cutoff_time:
                                size = os.path.getsize(file_path)

                                if dry_run:
                                    print(f"Would remove: {file_path} ({size/(1024**2):.1f}MB)")
                                else:
                                    os.remove(file_path)

                                removed_count += 1
                                freed_bytes += size
                        except Exception as e:
                            print(f"⚠️  Failed to process {file_path}: {e}")

        except Exception as e:
            print(f"⚠️  Error in {log_dir}: {e}")

    action = "Would free" if dry_run else "Freed"
    print(f"✅ {action} {freed_bytes/(1024**2):.1f}MB by removing {removed_count} log files")

    return removed_count, freed_bytes


def cleanup_database(dry_run=False):
    """Clean up old metrics from database."""
    db_path = "/data/anomstack.db"
    if not os.path.exists(db_path):
        print("❌ Database does not exist")
        return 0

    print("🧹 Cleaning old metrics from database...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Remove metrics older than 90 days
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # Get count before deletion
        cursor.execute("SELECT COUNT(*) FROM metrics WHERE metric_timestamp < ?", (cutoff_date,))
        old_count = cursor.fetchone()[0]

        if old_count == 0:
            print("✅ No old metrics to remove")
            conn.close()
            return 0

        if dry_run:
            print(f"Would remove {old_count} metrics older than {cutoff_date}")
        else:
            # Delete old metrics
            cursor.execute("DELETE FROM metrics WHERE metric_timestamp < ?", (cutoff_date,))

            # Vacuum to reclaim space
            print("Running VACUUM to reclaim space...")
            cursor.execute("VACUUM")

            conn.commit()
            print(f"✅ Removed {old_count} old metrics and vacuumed database")

        conn.close()
        return old_count

    except Exception as e:
        print(f"❌ Database cleanup error: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Clean up disk space on Fly.io instances")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be deleted without deleting"
    )
    parser.add_argument(
        "--aggressive", action="store_true", help="Use more aggressive cleanup settings"
    )

    args = parser.parse_args()

    print("🚀 Anomstack Disk Space Cleanup")
    print("=" * 40)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
    if args.aggressive:
        print("⚡ AGGRESSIVE MODE - More thorough cleanup")

    print()

    # Show initial disk usage
    print("📊 Initial disk usage:")
    usage = get_disk_usage()
    if usage:
        print(f"   Total: {usage['total_gb']:.1f}GB")
        print(f"   Used:  {usage['used_gb']:.1f}GB ({usage['usage_percent']:.1f}%)")
        print(f"   Free:  {usage['free_gb']:.1f}GB")
    print()

    # Perform cleanup
    total_files_removed = 0
    total_bytes_freed = 0

    # Clean artifacts
    art_count, art_bytes = cleanup_artifacts(args.dry_run, args.aggressive)
    total_files_removed += art_count
    total_bytes_freed += art_bytes
    print()

    # Clean logs
    log_count, log_bytes = cleanup_logs(args.dry_run, args.aggressive)
    total_files_removed += log_count
    total_bytes_freed += log_bytes
    print()

    # Clean database
    db_count = cleanup_database(args.dry_run)
    print()

    # Show final results
    print("📊 Final disk usage:")
    usage = get_disk_usage()
    if usage:
        print(f"   Total: {usage['total_gb']:.1f}GB")
        print(f"   Used:  {usage['used_gb']:.1f}GB ({usage['usage_percent']:.1f}%)")
        print(f"   Free:  {usage['free_gb']:.1f}GB")

    print()
    print("🎉 Cleanup Summary:")
    action = "Would remove" if args.dry_run else "Removed"
    print(f"   {action} {total_files_removed} files/directories")
    print(f"   {action} {db_count} database records")
    action2 = "Would free" if args.dry_run else "Freed"
    print(f"   {action2} {total_bytes_freed/(1024**2):.1f}MB of disk space")

    if not args.dry_run and usage and usage["usage_percent"] > 90:
        print()
        print("⚠️  WARNING: Disk usage still high after cleanup!")
        print("   Consider scaling up your Fly volume or more aggressive cleanup")


if __name__ == "__main__":
    main()
