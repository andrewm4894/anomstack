from dagster import (
    asset,
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
    FilesystemIOManager,
    EnvVar
)


@asset
def dev1():
    """
    """
    return 'dev'


@asset
def dev2(context, dev1):
    """
    """
    context.log.info(f'dev1: {dev1}')
    return 'dev'


dev_job = define_asset_job('dev_job', selection='dev2')
dev_schedule = ScheduleDefinition(
    job=dev_job,
    cron_schedule='*/5 * * * *',
)
file_io_manager = FilesystemIOManager(
    base_dir='data',
)
defs = Definitions(
    assets=[dev1, dev2],
    schedules=[dev_schedule],
    resources={
        "io_manager": file_io_manager,
    },
)
