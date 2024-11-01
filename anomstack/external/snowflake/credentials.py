"""
Some helper functions for getting Snowflake credentials.
"""

import os
from typing import Dict


def get_snowflake_credentials() -> Dict[str, str]:
    """
    Retrieves the Snowflake credentials from environment variables.

    Returns:
        dict: A dictionary containing the Snowflake credentials.
            - snowflake_account (str): The Snowflake account name.
            - snowflake_user (str): The Snowflake username.
            - snowflake_password (str): The Snowflake password.
            - snowflake_warehouse (str): The Snowflake warehouse name.
    """
    snowflake_account: str = os.getenv("ANOMSTACK_SNOWFLAKE_ACCOUNT")
    snowflake_user: str = os.getenv("ANOMSTACK_SNOWFLAKE_USER")
    snowflake_password: str = os.getenv("ANOMSTACK_SNOWFLAKE_PASSWORD")
    snowflake_warehouse: str = os.getenv("ANOMSTACK_SNOWFLAKE_WAREHOUSE")

    snowflake_credentials: Dict[str, str] = {
        "snowflake_account": snowflake_account,
        "snowflake_user": snowflake_user,
        "snowflake_password": snowflake_password,
        "snowflake_warehouse": snowflake_warehouse,
    }

    return snowflake_credentials
