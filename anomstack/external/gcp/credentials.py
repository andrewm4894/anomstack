"""
Some helper functions for retrieving Google credentials.
"""

import json
import os

from google.oauth2 import service_account

from dagster import get_dagster_logger


def get_google_credentials():
    """
    Attempt to retrieve Google credentials from environment variables.

    First, try to get a file path from GOOGLE_APPLICATION_CREDENTIALS and load
    credentials from it. If that fails, try to load credentials from a JSON
    string in GOOGLE_APPLICATION_CREDENTIALS_JSON.

    Returns:
        google.auth.credentials.Credentials or None: Google credentials or
        None if credentials cannot be retrieved or parsed.
    """

    logger = get_dagster_logger()

    # Check for file path credentials
    credentials_path = os.getenv("ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS")
    credentials = None

    if credentials_path:
        try:
            credentials = service_account.Credentials.\
                from_service_account_file(credentials_path)
            logger.info(f"Loaded credentials from file path: {credentials_path}")
        except Exception as e:
            logger.info(
                (
                    f"Failed to load credentials from file with: {str(e)}. "
                    "Trying to load from JSON string..."
                )
            )

    # If credentials could not be loaded from file path, try JSON string
    if credentials is None:
        raw_credentials = os.getenv("ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS_JSON")

        if raw_credentials:
            try:
                credentials_json = json.loads(raw_credentials)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_json
                )
                logger.info("Loaded credentials from JSON string")
            except json.JSONDecodeError as e:
                logger.info(f"Failed to parse JSON credentials with: {str(e)}")

    return credentials
