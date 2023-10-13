import os


def get_snowflake_credentials():

    snowflake_account = os.getenv('ANOMSTACK_SNOWFLAKE_ACCOUNT')
    snowflake_user = os.getenv('ANOMSTACK_SNOWFLAKE_USER')
    snowflake_password = os.getenv('ANOMSTACK_SNOWFLAKE_PASSWORD')
    snowflake_warehouse = os.getenv('ANOMSTACK_SNOWFLAKE_WAREHOUSE')

    snowflake_credentials = {
        'snowflake_account': snowflake_account,
        'snowflake_user': snowflake_user,
        'snowflake_password': snowflake_password,
        'snowflake_warehouse': snowflake_warehouse,
    }

    return snowflake_credentials
