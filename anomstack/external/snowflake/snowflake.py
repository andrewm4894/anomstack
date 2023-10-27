"""
"""

from dagster import get_dagster_logger
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
from anomstack.external.snowflake.credentials import get_snowflake_credentials


def read_sql_snowflake(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """

    logger = get_dagster_logger()

    logger.debug(f'sql:\n{sql}')

    credentials = get_snowflake_credentials()

    conn = snowflake.connector.connect(
        account=credentials['snowflake_account'],
        user=credentials['snowflake_user'],
        password=credentials['snowflake_password'],
        warehouse=credentials['snowflake_warehouse'],
    )
    cur = conn.cursor()
    cur.execute(sql)
    df = cur.fetch_pandas_all()

    logger.debug(f'df:\n{df}')

    return df


def save_df_snowflake(df, table_key) -> pd.DataFrame:
    """
    Save df to db.
    """

    logger = get_dagster_logger()

    table_key_parts = table_key.split('.')

    credentials = get_snowflake_credentials()

    conn = snowflake.connector.connect(
        account=credentials['snowflake_account'],
        user=credentials['snowflake_user'],
        password=credentials['snowflake_password'],
        warehouse=credentials['snowflake_warehouse'],
    )
    success, nchunks, nrows, _ = write_pandas(
        conn,
        df,
        database=table_key_parts[0],
        schema=table_key_parts[1],
        table_name=table_key_parts[2],
        auto_create_table=True
    )

    conn.close()

    return df
