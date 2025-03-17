"""
Data manager for the dashboard.
"""

import pandas as pd
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
import re
from datetime import datetime, timedelta


def parse_time_spec(spec_str: str) -> dict:
    """
    Parse a time specification string into a dictionary with type and value.
    Supports formats:
    - "30N" or "30n" for last N observations
    - "24h" for last 24 hours
    - "45m" for last 45 minutes
    - "7d" for last 7 days
    
    Returns:
        dict with keys:
        - 'type': 'n' for observations, 'time' for time-based
        - 'value': number of observations or timedelta object
    """
    if not spec_str:
        return {'type': 'n', 'value': DEFAULT_LAST_N}
    
    # Convert to string if number passed
    spec_str = str(spec_str).strip().lower()
    
    # Match patterns
    n_pattern = re.match(r'^(\d+)n$', spec_str)
    time_pattern = re.match(r'^(\d+)([hmd])$', spec_str)
    
    if n_pattern:
        return {'type': 'n', 'value': int(n_pattern.group(1))}
    
    if time_pattern:
        value = int(time_pattern.group(1))
        unit = time_pattern.group(2)
        
        delta = {
            'm': timedelta(minutes=value),
            'h': timedelta(hours=value),
            'd': timedelta(days=value)
        }[unit]
        
        return {'type': 'time', 'value': delta}
    
    # Try to parse as plain number for backward compatibility
    try:
        return {'type': 'n', 'value': int(spec_str)}
    except ValueError:
        raise ValueError(
            f"Invalid time specification: {spec_str}. "
            "Use format: 30n (observations), 24h (hours), 45m (minutes), 7d (days)"
        )

def get_data(spec: dict, last_n: str = "30n", ensure_timestamp: bool = False) -> pd.DataFrame:
    """
    Get data from the database for a given spec and time specification.
    
    Args:
        spec: The spec to get data for.
        last_n: Time specification (e.g., "30n", "24h", "45m", "7d")
        ensure_timestamp: Whether to ensure timestamp column exists
        
    Returns:
        A pandas DataFrame containing the data.
    """
    time_spec = parse_time_spec(last_n)
    
    if time_spec['type'] == 'time':
        # For time-based queries
        cutoff_time = datetime.now() - time_spec['value']
        sql = render(
            "dashboard_sql",
            spec,
            params={
                "last_n": None,
                "cutoff_time": cutoff_time.isoformat()
            }
        )
    else:
        # For N-based queries
        sql = render(
            "dashboard_sql",
            spec,
            params={
                "last_n": time_spec['value'],
                "cutoff_time": None
            }
        )
    
    db = spec["db"]
    try:
        df = read_sql(sql, db=db)
        # Filter out rows with NULL timestamps or values
        df = df.dropna(subset=['metric_timestamp', 'metric_value'])
        if df.empty:
            return pd.DataFrame(columns=['metric_timestamp', 'metric_batch', 'metric_name', 'metric_value'])
    except Exception as e:
        logging.error(f"Error reading data: {e}")
        return pd.DataFrame(columns=['metric_timestamp', 'metric_batch', 'metric_name', 'metric_value'])

    if ensure_timestamp:
        df["metric_timestamp"] = pd.to_datetime(df["metric_timestamp"], errors="coerce")
        df = df.sort_values("metric_timestamp")
    
    return df
