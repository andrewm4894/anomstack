"""
Data manager for the dashboard.
"""

import pandas as pd
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql


def get_data(spec: dict, last_n: int = 30, ensure_timestamp: bool = False) -> pd.DataFrame:
    """
    Get data from the database for a given spec and last_n.
    
    Args:
        spec: The spec to get data for.
        last_n: The maximum number of observations to return.
        
    Returns:
        A pandas DataFrame containing the data.
    """
    sql = render(
        "dashboard_sql",
        spec,
        params={"last_n": last_n},
    )
    db = spec["db"]
    df = read_sql(sql, db=db)

    if ensure_timestamp:
        df["metric_timestamp"] = pd.to_datetime(df["metric_timestamp"], errors="coerce")
        df = df.sort_values("metric_timestamp")
    
    return df
