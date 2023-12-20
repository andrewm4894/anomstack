"""
"""

import pandas as pd
import snowflake.connector
from dagster import get_dagster_logger
from snowflake.connector.pandas_tools import write_pandas

from anomstack.external.snowflake.credentials import get_snowflake_credentials


def read_sql_snowflake(sql, cols_lowercase=True) -> pd.DataFrame:
    """
    Read data from SQL.
    """

    logger = get_dagster_logger()

    logger.debug(f"sql:\n{sql}")

    credentials = get_snowflake_credentials()

    conn = snowflake.connector.connect(
        account=credentials["snowflake_account"],
        user=credentials["snowflake_user"],
        password=credentials["snowflake_password"],
        warehouse=credentials["snowflake_warehouse"],
    )
    cur = conn.cursor()
    cur.execute(sql)
    df = cur.fetch_pandas_all()

    if cols_lowercase:
        df.columns = df.columns.str.lower()

    logger.debug(f"df:\n{df}")

    return df


def save_df_snowflake(df, table_key, cols_lowercase=True) -> pd.DataFrame:
    """
    Save df to db.
    """

    logger = get_dagster_logger()

    table_key_parts = table_key.split(".")

    credentials = get_snowflake_credentials()

    conn = snowflake.connector.connect(
        account=credentials["snowflake_account"],
        user=credentials["snowflake_user"],
        password=credentials["snowflake_password"],
        warehouse=credentials["snowflake_warehouse"],
    )

    # convert metric timestamp to string
    # fixes: nowflake.connector.errors.ProgrammingError: 002023 (22000): SQL compilation error: Expression type does not match column data type, expecting TIMESTAMP_NTZ(9) but got NUMBER(38,0) for column METRIC_TIMESTAMP
    # TODO: why do i have to do this?
    df["metric_timestamp"] = df["metric_timestamp"].astype(str)

    success, nchunks, nrows, output = write_pandas(
        conn,
        df,
        database=table_key_parts[0],
        schema=table_key_parts[1],
        table_name=table_key_parts[2],
        auto_create_table=True,
    )

    conn.close()

    if cols_lowercase:
        df.columns = df.columns.str.lower()

    return df
