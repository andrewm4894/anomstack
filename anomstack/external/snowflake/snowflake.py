"""
Some utilities for working with Snowflake.
"""

import pandas as pd
from snowflake import connector

from anomstack.external.snowflake.credentials import get_snowflake_credentials


def read_sql_snowflake(sql: str, cols_lowercase: bool = True) -> pd.DataFrame:
    """
    Read data from SQL.

    Args:
        sql (str): The SQL query to execute.
        cols_lowercase (bool, optional): Whether to convert column names
        to lowercase. Defaults to True.

    Returns:
        pd.DataFrame: The result of the SQL query as a pandas DataFrame.
    """
    credentials = get_snowflake_credentials()

    conn = connector.connect(
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

    return df


def save_df_snowflake(
    df: pd.DataFrame, table_key: str, cols_lowercase: bool = True
) -> pd.DataFrame:
    """
    Save df to db.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        table_key (str): The key of the table in the format
            "database.schema.table".
        cols_lowercase (bool, optional): Whether to convert column names
            to lowercase. Defaults to True.

    Returns:
        pd.DataFrame: The input DataFrame.
    """

    table_key_parts = table_key.split(".")

    credentials = get_snowflake_credentials()

    conn = connector.connect(
        account=credentials["snowflake_account"],
        user=credentials["snowflake_user"],
        password=credentials["snowflake_password"],
        warehouse=credentials["snowflake_warehouse"],
    )

    # convert metric timestamp to string
    # fixes: snowflake.connector.errors.ProgrammingError: 002023 (22000):
    # SQL compilation error: Expression type does not match column data type,
    # expecting TIMESTAMP_NTZ(9) but got NUMBER(38,0) for column METRIC_TIMESTAMP
    # TODO: why do i have to do this?
    df["metric_timestamp"] = df["metric_timestamp"].astype(str)

    success, nchunks, nrows, output = connector.pandas_tools.write_pandas(
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
