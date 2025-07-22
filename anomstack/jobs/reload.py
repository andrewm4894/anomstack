"""
Generate configuration reload jobs and schedules.
"""

import os

from dagster import (
    MAX_RUNTIME_SECONDS_TAG,
    DefaultScheduleStatus,
    JobDefinition,
    ScheduleDefinition,
    get_dagster_logger,
    job,
    op,
)

from anomstack.config import execute_config_reload

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_config_reload_job() -> JobDefinition:
    """
    Build job definition for configuration reload job.

    This job automatically reloads Dagster configurations when run,
    allowing for hot updates without container restarts.

    Returns:
        JobDefinition: A job definition for the config reload job.
    """

    @job(
        name="config_reload",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Reload Dagster configuration from updated YAML files.
        """

        @op(name="reload_configuration")
        def reload_configuration() -> str:
            """
            Execute the configuration reload.

            Returns:
                str: Result of the reload operation.
            """
            import os
            logger = get_dagster_logger()

            logger.info("🔄 Starting configuration reload via Dagster job...")

            # Ensure environment variables are set for Dagster execution context
            # These might not be available when running as a scheduled job
            if not os.getenv("DAGSTER_HOST"):
                os.environ["DAGSTER_HOST"] = "anomstack_webserver"
                logger.info("🔧 Set DAGSTER_HOST=anomstack_webserver for job execution")

            if not os.getenv("DAGSTER_PORT"):
                os.environ["DAGSTER_PORT"] = "3000"
                logger.info("🔧 Set DAGSTER_PORT=3000 for job execution")

            logger.info(f"🌐 Using Dagster host: {os.getenv('DAGSTER_HOST')}:{os.getenv('DAGSTER_PORT')}")

            # Execute the reload using the internal function
            success = execute_config_reload()

            if success:
                logger.info("✅ Configuration reload completed successfully")
                return "Configuration reload completed successfully"
            else:
                error_msg = "Configuration reload failed"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)

        reload_configuration()

    return _job


def should_enable_config_reload_job() -> bool:
    """
    Determine if the config reload job should be enabled.

    Returns:
        bool: True if the job should be enabled.
    """
    # Check environment variable to enable/disable the feature
    enabled = os.getenv("ANOMSTACK_AUTO_CONFIG_RELOAD", "false").lower() == "true"

    # Also check if we're in development mode
    dev_mode = os.getenv("DAGSTER_DEV", "false").lower() == "true"

    return enabled or dev_mode


# Build config reload job and schedule
reload_jobs = []
reload_schedules = []

if should_enable_config_reload_job():
    logger = get_dagster_logger()
    logger.info("🔧 Config reload job is enabled")

    config_reload_job = build_config_reload_job()
    reload_jobs.append(config_reload_job)

    # Get reload schedule from environment or default to every 5 minutes
    reload_cron_schedule = os.getenv("ANOMSTACK_CONFIG_RELOAD_CRON", "*/5 * * * *")
    reload_default_status = os.getenv("ANOMSTACK_CONFIG_RELOAD_STATUS", "STOPPED")

    if reload_default_status == "RUNNING":
        reload_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        reload_default_schedule_status = DefaultScheduleStatus.STOPPED

    config_reload_schedule = ScheduleDefinition(
        job=config_reload_job,
        cron_schedule=reload_cron_schedule,
        default_status=reload_default_schedule_status,
    )
    reload_schedules.append(config_reload_schedule)

    logger.info(f"📅 Config reload scheduled: {reload_cron_schedule} (status: {reload_default_status})")
else:
    logger = get_dagster_logger()
    logger.info("⏸️ Config reload job is disabled (set ANOMSTACK_AUTO_CONFIG_RELOAD=true to enable)")
