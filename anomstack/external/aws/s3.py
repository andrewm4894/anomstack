import pickle
from typing import List, Tuple

import boto3
from dagster import get_dagster_logger
from pyod.models.base import BaseDetector

from anomstack.external.aws.credentials import get_aws_credentials


def split_model_path(model_path: str) -> Tuple[str, str]:
    model_path_parts = model_path.split("://")
    model_path_bucket = model_path_parts[1].split("/")[0]
    model_path_prefix = "/".join(model_path_parts[1].split("/")[1:])
    return model_path_bucket, model_path_prefix


def get_s3_client():
    aws_credentials = get_aws_credentials()
    return boto3.client(
        "s3",
        aws_access_key_id=aws_credentials["aws_access_key_id"],
        aws_secret_access_key=aws_credentials["aws_secret_access_key"],
    )


def save_models_s3(models, model_path, metric_batch) -> List[Tuple[str, BaseDetector]]:
    logger = get_dagster_logger()
    model_path_bucket, model_path_prefix = split_model_path(model_path)

    s3_client = get_s3_client()

    for metric, model in models:
        model_name = f"{metric}.pkl"
        logger.info(f"saving {model_name} to {model_path}")

        model_byte_stream = pickle.dumps(model)
        s3_client.put_object(
            Body=model_byte_stream,
            Bucket=model_path_bucket,
            Key=f"{model_path_prefix}/{metric_batch}/{model_name}",
        )

    return models


def load_model_s3(metric_name, model_path, metric_batch) -> BaseDetector:
    logger = get_dagster_logger()
    model_path_bucket, model_path_prefix = split_model_path(model_path)

    model_name = f"{metric_name}.pkl"
    logger.info(f"loading {model_name} from {model_path}")

    s3_client = get_s3_client()

    model_obj = s3_client.get_object(
        Bucket=model_path_bucket, Key=f"{model_path_prefix}/{metric_batch}/{model_name}"
    )

    model_byte_stream = model_obj["Body"].read()
    model = pickle.loads(model_byte_stream)

    return model
