"""
Some helper functions to get AWS credentials from the environment.
"""

import os


def get_aws_credentials():
    """
    Retrieves AWS credentials from environment variables.

    Returns:
        dict: A dictionary containing the AWS access key ID and secret access key.
    Raises:
        ValueError: If the environment variables are not found.
    """
    aws_access_key_id = os.getenv("ANOMSTACK_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("ANOMSTACK_AWS_SECRET_ACCESS_KEY")

    if aws_access_key_id is None or aws_secret_access_key is None:
        raise ValueError("AWS credentials not found in environment variables.")

    aws_credentials = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
    }

    return aws_credentials
