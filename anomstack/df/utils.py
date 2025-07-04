from io import StringIO

import pandas as pd
from dagster import get_dagster_logger


def log_df_info(df: pd.DataFrame, logger=None):
    """
    Logs the info of a DataFrame to the logger.

    Parameters:
    df (pd.DataFrame): The DataFrame whose info needs to be logged.
    """
    if not logger:
        logger = get_dagster_logger()
    buffer = StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    logger.info("df.info():\n%s", info_str)


def generate_insert_sql(df, table_name, batch_size=100) -> list[str]:
    """Generate batched INSERT statements from DataFrame."""
    columns = ', '.join(df.columns)
    insert_sqls = []
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        values_list = []
        for _, row in batch.iterrows():
            row_values = []
            for val in row:
                if isinstance(val, str) or isinstance(val, pd.Timestamp):
                    row_values.append(f'\'{val}\'')
                else:
                    row_values.append(str(val))
            values_list.append(f"({', '.join(row_values)})")
        values = ', '.join(values_list)
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES {values};"
        insert_sqls.append(insert_sql)

    return insert_sqls
