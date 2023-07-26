import os
from dagster import Config


specs = {
    "m1": {
        "name": "m1",
        "ingest": {
            "name": "m1",
            "sql": """
            select
                current_timestamp() as timestamp,
                'metric_1' as name,
                rand() as value,
            """,
            "cron_schedule": "*/2 * * * *",
            "dataset": "tmp", 
            "table": "metrics",
            "bucket_name": os.getenv("GCS_BUCKET_NAME"),
            "project_id": os.getenv("GCS_PROJECT_ID"),
        },
        "train": {
            "name": "m1",
            "sql": """
            select
                *
            from
                tmp.metrics
            where
                name = 'metric_1'
            order by timestamp desc
            limit 1000
            """,
            "cron_schedule": "*/4 * * * *",
            "dataset": "tmp", 
            "table": "metrics",
            "bucket_name": os.getenv("GCS_BUCKET_NAME"),
            "project_id": os.getenv("GCS_PROJECT_ID"),
        },
        "score": {
            "name": "m1",
            "sql": """
            select
                *
            from
                tmp.metrics
            where
                name = 'metric_1'
            order by timestamp desc
            limit 1
            """,
            "cron_schedule": "*/3 * * * *",
            "dataset": "tmp", 
            "table": "metrics",
            "bucket_name": os.getenv("GCS_BUCKET_NAME"),
            "project_id": os.getenv("GCS_PROJECT_ID"),
        }
    },
    "m2": {
        "name": "m2",
        "ingest": {
            "name": "m2",
            "sql": """
            select
                current_timestamp() as timestamp,
                'metric_2' as name,
                rand() as value,
            """,
            "cron_schedule": "*/3 * * * *",
            "dataset": "tmp", 
            "table": "metrics",
            "project_id": os.getenv("GCS_PROJECT_ID"),
        },
        "train": {
            "name": "m2",
            "sql": """
            select
                *
            from
                tmp.metrics
            where
                name = 'metric_2'
            order by timestamp desc
            limit 1000
            """,
            "cron_schedule": "*/5 * * * *",
            "bucket_name": os.getenv("GCS_BUCKET_NAME"),
            "project_id": os.getenv("GCS_PROJECT_ID"),
        },
        "score": {
            "name": "m2",
            "sql": """
            select
                *
            from
                tmp.metrics
            where
                name = 'metric_2'
            order by timestamp desc
            limit 1
            """,
            "cron_schedule": "*/4 * * * *",
            "dataset": "tmp", 
            "table": "metrics",
            "bucket_name": os.getenv("GCS_BUCKET_NAME"),
            "project_id": os.getenv("GCS_PROJECT_ID"),
        }
    },
}
