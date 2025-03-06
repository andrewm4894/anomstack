"""
Data manager for the dashboard.
"""

import pandas as pd
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql


def get_data(spec: dict, max_n: int = 30, ensure_timestamp: bool = False) -> pd.DataFrame:
    """
    Get data from the database for a given spec and max_n.
    
    Args:
        spec: The spec to get data for.
        max_n: The maximum number of alerts to return.
        
    Returns:
        A pandas DataFrame containing the data.
    """
    sql = render(
        "dashboard_sql",
        spec,
        params={"alert_max_n": max_n},
    )
    db = spec["db"]
    df = read_sql(sql, db=db)

    if ensure_timestamp:
        df["metric_timestamp"] = pd.to_datetime(df["metric_timestamp"], errors="coerce")
        df = df.sort_values("metric_timestamp")
    
    return df
