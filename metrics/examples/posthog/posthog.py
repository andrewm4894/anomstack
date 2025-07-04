import os

import pandas as pd


def ingest() -> pd.DataFrame:
    """Ingest headline metrics from the PostHog query API."""
    import requests
    from dagster import get_dagster_logger

    logger = get_dagster_logger()

    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    if not api_key or not project_id:
        raise RuntimeError(
            "POSTHOG_API_KEY and POSTHOG_PROJECT_ID env vars must be set"
        )

    host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
    url = f"{host}/api/projects/{project_id}/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    query = """
        SELECT
            count() AS events_yesterday,
            count(DISTINCT person_id) AS users_yesterday
        FROM events
        WHERE timestamp >= toStartOfDay(now() - INTERVAL 1 day)
          AND timestamp < toStartOfDay(now())
    """

    try:
        response = requests.post(
            url, headers=headers, json={"query": query}, timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as ex:
        logger.error(f"Failed to fetch PostHog data from {url}: {ex}")
        return pd.DataFrame(columns=["metric_timestamp", "metric_name", "metric_value"])

    data = response.json()

    rows = []
    ts = pd.Timestamp.utcnow().floor("s")
    results = data.get("results") or data.get("data")
    if results:
        first = results[0]
        if isinstance(first, dict):
            events = first.get("events_yesterday")
            users = first.get("users_yesterday")
        elif isinstance(first, list):
            columns = data.get("columns", [])
            try:
                events = first[columns.index("events_yesterday")]
            except (ValueError, IndexError):
                events = first[0]
            try:
                users = first[columns.index("users_yesterday")]
            except (ValueError, IndexError):
                users = first[1] if len(first) > 1 else None
        else:
            events = users = None

        if events is not None:
            rows.append(
                {
                    "metric_timestamp": ts,
                    "metric_name": "posthog.events_yesterday",
                    "metric_value": float(events),
                }
            )
        if users is not None:
            rows.append(
                {
                    "metric_timestamp": ts,
                    "metric_name": "posthog.users_yesterday",
                    "metric_value": float(users),
                }
            )

    df = pd.DataFrame(rows)
    df = df.dropna()
    df = df[["metric_timestamp", "metric_name", "metric_value"]]
    return df
