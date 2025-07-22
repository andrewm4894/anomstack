"""
Sensor for automatic configuration reloading when YAML files change.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from dagster import (
    SensorEvaluationContext,
    SkipReason,
    get_dagster_logger,
    sensor,
)

from anomstack.config import execute_config_reload


def get_metrics_directory() -> Path:
    """Get the metrics directory path."""
    return Path("./metrics").resolve()


def calculate_directory_hash(directory: Path) -> str:
    """
    Calculate a hash of all YAML files in the metrics directory.

    Args:
        directory: Path to the metrics directory

    Returns:
        str: MD5 hash of all YAML file contents and modification times
    """
    hash_md5 = hashlib.md5()

    try:
        # Get all YAML files recursively, sorted for consistent hashing
        yaml_files = sorted(directory.rglob("*.yaml"))

        for yaml_file in yaml_files:
            try:
                # Include file path in hash
                hash_md5.update(str(yaml_file.relative_to(directory)).encode())

                # Include modification time
                mtime = yaml_file.stat().st_mtime
                hash_md5.update(str(mtime).encode())

                # Include file content
                with open(yaml_file, 'rb') as f:
                    hash_md5.update(f.read())

            except (OSError, IOError) as e:
                # File might have been deleted or is unreadable, skip it
                hash_md5.update(f"ERROR:{e}".encode())

        return hash_md5.hexdigest()

    except Exception as e:
        # Return a hash that includes the error for consistency
        return hashlib.md5(f"ERROR:{e}".encode()).hexdigest()


def get_stored_hash(context: SensorEvaluationContext) -> Optional[str]:
    """Get the last stored directory hash from sensor context."""
    cursor = context.cursor
    if cursor:
        try:
            cursor_data = json.loads(cursor)
            return cursor_data.get("last_hash")
        except (json.JSONDecodeError, KeyError):
            return None
    return None


def store_hash(context: SensorEvaluationContext, directory_hash: str) -> str:
    """Store the directory hash in sensor context."""
    return json.dumps({"last_hash": directory_hash})


def execute_sensor_config_reload() -> bool:
    """
    Execute the configuration reload via sensor.

    Returns:
        bool: True if reload was successful, False otherwise
    """
    logger = get_dagster_logger()

    try:
        logger.info("🔄 Executing configuration reload via sensor...")

        # Use the internal reload function
        return execute_config_reload()

    except Exception as e:
        logger.error(f"💥 Unexpected error during configuration reload: {str(e)}")
        return False


def should_enable_config_watcher() -> bool:
    """
    Determine if the config watcher sensor should be enabled.

    Returns:
        bool: True if the sensor should be enabled.
    """
    # Check environment variable to enable/disable the feature
    enabled = os.getenv("ANOMSTACK_CONFIG_WATCHER", "false").lower() == "true"

    # Also check if we're in development mode
    dev_mode = os.getenv("DAGSTER_DEV", "false").lower() == "true"

    return enabled or dev_mode


# Get sensor configuration
SENSOR_ENABLED = should_enable_config_watcher()
SENSOR_INTERVAL = int(os.getenv("ANOMSTACK_CONFIG_WATCHER_INTERVAL", "30"))  # seconds

if SENSOR_ENABLED:
    @sensor(
        name="config_file_watcher",
        minimum_interval_seconds=SENSOR_INTERVAL,
    )
    def config_file_watcher(context: SensorEvaluationContext):
        """
        Watch for changes to YAML configuration files and reload when necessary.

        This sensor monitors the metrics directory for changes to .yaml files
        and triggers a configuration reload when changes are detected.
        """
        logger = get_dagster_logger()

        try:
            metrics_dir = get_metrics_directory()

            if not metrics_dir.exists():
                return SkipReason(f"Metrics directory not found: {metrics_dir}")

            # Calculate current hash of all YAML files
            current_hash = calculate_directory_hash(metrics_dir)
            last_hash = get_stored_hash(context)

            # Check if this is the first run
            if last_hash is None:
                logger.info("🔍 First run of config file watcher - storing initial hash")
                context.update_cursor(store_hash(context, current_hash))
                return SkipReason("First run - establishing baseline")

            # Check if files have changed
            if current_hash == last_hash:
                return SkipReason("No configuration file changes detected")

            logger.info("📝 Configuration file changes detected!")
            logger.info(f"Previous hash: {last_hash[:8]}...")
            logger.info(f"Current hash:  {current_hash[:8]}...")

            # Execute the reload
            reload_success = execute_sensor_config_reload()

            if reload_success:
                # Update cursor with new hash only if reload was successful
                context.update_cursor(store_hash(context, current_hash))
                logger.info("🎉 Configuration watcher successfully reloaded configs")
                return SkipReason("Configuration reloaded successfully")
            else:
                logger.error("❌ Configuration reload failed - keeping old hash")
                return SkipReason("Configuration reload failed")

        except Exception as e:
            logger.error(f"💥 Error in config file watcher: {str(e)}")
            return SkipReason(f"Sensor error: {str(e)}")
else:
    # Create a dummy sensor that's always disabled
    @sensor(
        name="config_file_watcher_disabled",
        minimum_interval_seconds=3600,  # Check once per hour
    )
    def config_file_watcher(context: SensorEvaluationContext):
        """Disabled config file watcher."""
        return SkipReason("Config file watcher is disabled (set ANOMSTACK_CONFIG_WATCHER=true to enable)")
