"""
Helper functions for SQLite (or Turso) with retry logic.
"""

import os
import time
from contextlib import contextmanager

import libsql_experimental as libsql
import pandas as pd
from dagster import get_dagster_logger

from anomstack.df.utils import generate_insert_sql
from anomstack.sql.utils import get_columns_from_sql

MAX_RETRIES = 5
RETRY_DELAY = 1


def get_sqlite_path() -> str:
    """
    Returns the path to the SQLite (or Turso) database,
    creating directories if needed.

    By default, uses the env var ANOMSTACK_SQLITE_PATH,
    or falls back to "tmpdata/anomstack-sqlite.db".
    """
    default_path = "tmpdata/anomstack-sqlite.db"
    path = os.environ.get("ANOMSTACK_SQLITE_PATH", default_path)
    # If not a Turso URI, create directories for local DB path
    if not path.endswith("turso.io"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def get_conn(sqlite_path: str) -> libsql.Connection:
    """
    Get a connection to the SQLite or Turso database.

    If the path ends with 'turso.io', it uses the
    ANOMSTACK_TURSO_DATABASE_URL and ANOMSTACK_TURSO_AUTH_TOKEN
    environment variables for authentication.
    Otherwise, it connects to a local SQLite database.

    Args:
        sqlite_path (str): The path or URL of the database.

    Returns:
        libsql.Connection: The connection object.
    """
    if sqlite_path.endswith("turso.io"):
        url = os.environ.get("ANOMSTACK_TURSO_DATABASE_URL", None)
        auth_token = os.environ.get("ANOMSTACK_TURSO_AUTH_TOKEN", None)
        return libsql.connect(sqlite_path, sync_url=url, auth_token=auth_token)
    else:
        return libsql.connect(sqlite_path)


def with_sqlite_retry(
    action,
    logger=None,
    max_retries=MAX_RETRIES,
    retry_delay=RETRY_DELAY,
):
    """
    Executes a callable with retry logic if the database is locked.

    Args:
        action (callable): A zero-argument function that performs the DB action
            and returns a value.
        logger (Logger, optional): Logger for logging warnings/errors.
            Defaults to ``None``.
        max_retries (int, optional): Maximum number of retries. Defaults to
            ``MAX_RETRIES``.
        retry_delay (float, optional): Delay in seconds between retries.
            Defaults to ``RETRY_DELAY``.

    Returns:
        The result of 'action' if successful.

    Raises:
        Exception: If the database remains locked after all retries or another
            error occurs.
    """
    for attempt in range(max_retries):
        try:
            return action()
        except Exception as e:
            if "database is locked" in str(e):
                if logger:
                    logger.warning(
                        f"Database is locked; attempt {attempt + 1} of {max_retries}. "
                        f"Retrying in {retry_delay} seconds..."
                    )
                time.sleep(retry_delay)
            else:
                if logger:
                    logger.error(f"Error during DB action: {e}")
                raise
    raise Exception("Database is locked after multiple attempts.")


@contextmanager
def sqlite_connection():
    """
    Context manager that yields a DB connection, ensuring it is closed on exit.
    """
    path = get_sqlite_path()
    conn = get_conn(path)
    yield conn


def infer_sqlite_type(dtype) -> str:
    """
    Map pandas dtypes to SQLite types.

    Args:
        dtype: A pandas dtype (e.g. df.dtypes[col]).

    Returns:
        str: The corresponding SQLite type name.
    """
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "REAL"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TEXT"
    else:
        return "TEXT"


def generate_create_table_sql(df: pd.DataFrame, table_name: str) -> str:
    """
    Generate the CREATE TABLE statement for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame whose columns are used to infer table schema.
        table_name (str): The name of the table.

    Returns:
        str: The CREATE TABLE SQL statement.
    """
    column_defs = [
        f"{col} {infer_sqlite_type(dtype)}"
        for col, dtype in zip(df.columns, df.dtypes)
    ]
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)});"


def read_sql_sqlite(sql: str) -> pd.DataFrame:
    """
    Read data from SQLite (or Turso) with retry logic.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The result of the SQL query as a pandas DataFrame.
    """
    logger = get_dagster_logger()
    logger.info(f"Reading from DB path: {get_sqlite_path()}")

    def _action():
        with sqlite_connection() as conn:
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
            columns = (
                [desc[0] for desc in cursor.description]
                if cursor.description
                else get_columns_from_sql(sql)
            )
            return pd.DataFrame(rows, columns=columns)

    return with_sqlite_retry(_action, logger=logger)


def save_df_sqlite(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    """
    Save a DataFrame to the database (SQLite or Turso) with retry logic.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        table_key (str): The table name to save the DataFrame as.

    Returns:
        pd.DataFrame: The input DataFrame.
    """
    logger = get_dagster_logger()
    logger.info(f"Saving DataFrame to DB path: {get_sqlite_path()}")

    def _action():
        with sqlite_connection() as conn:
            create_table_sql = generate_create_table_sql(df, table_key)
            conn.execute(create_table_sql)
            insert_sqls = generate_insert_sql(df, table_key)
            for ins_sql in insert_sqls:
                conn.execute(ins_sql)
            conn.commit()
        return df

    return with_sqlite_retry(_action, logger=logger)


def run_sql_sqlite(sql: str, return_df: bool = False):
    """Execute a SQL statement with retry logic.

    When ``return_df`` is ``True``, the results of the statement are returned as a
    :class:`~pandas.DataFrame`.

    Args:
        sql (str): The SQL statement to execute.
        return_df (bool, optional): If ``True``, return the results as a
            DataFrame. Defaults to ``False``.

    Returns:
        Optional[pd.DataFrame]: A DataFrame of results when ``return_df`` is
        ``True``; otherwise ``None``.
    """
    logger = get_dagster_logger()
    logger.info(f"Executing SQL against DB path: {get_sqlite_path()}")

    def _action(return_df=return_df):
        with sqlite_connection() as conn:
            cursor = conn.execute(sql)
            conn.commit()
            rows = cursor.fetchall()
            columns = (
                [desc[0] for desc in cursor.description]
                if cursor.description
                else get_columns_from_sql(sql)
            )
            df = pd.DataFrame(rows, columns=columns)
            return df if return_df else None

    return with_sqlite_retry(_action, logger=logger)
