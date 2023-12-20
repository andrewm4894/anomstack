import os


def get_aws_credentials():
    aws_access_key_id = os.getenv("ANOMSTACK_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("ANOMSTACK_AWS_SECRET_ACCESS_KEY")

    aws_credentials = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
    }

    return aws_credentials
