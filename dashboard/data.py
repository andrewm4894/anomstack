"""
dashboard/data.py

Data manager for the dashboard.

This module contains functions for getting data from the database for the dashboard.

"""

from datetime import datetime, timedelta
import logging
import re
from typing import Union

import pandas as pd

from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from dashboard.constants import DEFAULT_LAST_N

log = logging.getLogger("anomstack_dashboard")


def parse_time_spec(spec_str: Union[str, int, None]) -> dict:
    """
    Parse a time specification string into a dictionary with type and value.
    Supports formats:
    - "90n" or "90n" for last N observations
    - "24h" for last 24 hours
    - "45m" for last 45 minutes
    - "7d" for last 7 days

    Returns:
        dict with keys:
        - 'type': 'n' for observations, 'time' for time-based
        - 'value': number of observations or timedelta object
    """
    if not spec_str:
        return {"type": "n", "value": DEFAULT_LAST_N}

    # Convert to string if number passed
    spec_str = str(spec_str).strip().lower()

    # Match patterns
    n_pattern = re.match(r"^(\d+)n$", spec_str)
    time_pattern = re.match(r"^(\d+)([hmd])$", spec_str)

    if n_pattern:
        return {"type": "n", "value": int(n_pattern.group(1))}

    if time_pattern:
        value = int(time_pattern.group(1))
        unit = time_pattern.group(2)

        delta = {
            "m": timedelta(minutes=value),
            "h": timedelta(hours=value),
            "d": timedelta(days=value),
        }[unit]

        return {"type": "time", "value": delta}

    # Try to parse as plain number for backward compatibility
    try:
        return {"type": "n", "value": int(spec_str)}
    except ValueError:
        raise ValueError(
            f"Invalid time specification: {spec_str}. "
            "Use format: 90n (observations), 24h (hours), 45m (minutes), 7d (days)"
        )


def get_data(spec: dict, last_n: str = "90n", ensure_timestamp: bool = False) -> pd.DataFrame:
    """
    Get data from the database for a given spec and time specification.

    Args:
        spec: The spec to get data for.
        last_n: Time specification (e.g., "90n", "24h", "45m", "7d")
        ensure_timestamp: Whether to ensure timestamp column exists

    Returns:
        A pandas DataFrame containing the data.
    """
    time_spec = parse_time_spec(last_n)

    if time_spec["type"] == "time":
        # For time-based queries, we'll need to modify the SQL
        cutoff_time = datetime.now() - time_spec["value"]
        sql = render("dashboard_sql", spec, params={"cutoff_time": cutoff_time.isoformat()})
    else:
        # For N-based queries, use existing logic
        sql = render(
            "dashboard_sql",
            spec,
            params={"last_n": time_spec["value"]},
        )

    db = spec["db"]
    df = read_sql(sql, db=db)

    if ensure_timestamp:
        df["metric_timestamp"] = pd.to_datetime(df["metric_timestamp"], errors="coerce")
        df = df.sort_values("metric_timestamp")

    if "metric_llmalert" in df.columns:
        df["metric_llmalert"] = df["metric_llmalert"].clip(upper=1)

    return df
