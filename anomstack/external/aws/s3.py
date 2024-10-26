"""
Some helper functions for loading and saving models to S3.
"""

import pickle
from typing import List, Tuple

import boto3
from pyod.models.base import BaseDetector

from anomstack.external.aws.credentials import get_aws_credentials
from dagster import get_dagster_logger


def split_model_path(model_path: str) -> Tuple[str, str]:
    """
    Split the S3 model path into bucket and prefix.

    Args:
        model_path (str): The S3 model path.

    Returns:
        Tuple[str, str]: The bucket and prefix of the model path.
    """
    model_path_parts = model_path.split("://")
    model_path_bucket = model_path_parts[1].split("/")[0]
    model_path_prefix = "/".join(model_path_parts[1].split("/")[1:])

    return model_path_bucket, model_path_prefix


def get_s3_client() -> boto3.client:
    """
    Get the S3 client.

    Returns:
        boto3.client: The S3 client.
    """
    aws_credentials = get_aws_credentials()

    return boto3.client(
        "s3",
        aws_access_key_id=aws_credentials["aws_access_key_id"],
        aws_secret_access_key=aws_credentials["aws_secret_access_key"],
    )


def save_models_s3(
    models: List[Tuple[str, BaseDetector]], model_path: str, metric_batch
) -> List[Tuple[str, BaseDetector]]:
    """
    Save models to S3.

    Args:
        models (List[Tuple[str, BaseDetector]]): The models to be saved.
        model_path (str): The S3 model path.
        metric_batch: The metric batch.

    Returns:
        List[Tuple[str, BaseDetector]]: The list of saved models.
    """
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


def load_model_s3(metric_name: str, model_path: str, metric_batch) -> BaseDetector:
    """
    Load a model from S3.

    Args:
        metric_name (str): The name of the metric.
        model_path (str): The S3 model path.
        metric_batch: The metric batch.

    Returns:
        BaseDetector: The loaded model.
    """
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
