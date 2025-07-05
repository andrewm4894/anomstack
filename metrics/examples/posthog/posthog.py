import os

import pandas as pd


def ingest() -> pd.DataFrame:
    """Ingest headline metrics from the PostHog query API for multiple projects/domains."""
    import requests
    import os
    from dagster import get_dagster_logger

    logger = get_dagster_logger()
    api_key = os.getenv("POSTHOG_API_KEY")
    if not api_key:
        raise RuntimeError("POSTHOG_API_KEY env var must be set")

    project_domain_map = {
        "1016": "andrewm4894.com",
        "140227": "anomstack-demo",
        "112495": "andys-daily-factoids.com",
        "148051": "andys-daily-riddle.com",
    }

    host = os.getenv("POSTHOG_HOST", "https://us.posthog.com")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    query = """
        SELECT
            count() AS events_yday,
            count(DISTINCT person_id) AS users_yday,
            countIf(event = '$pageview') AS pageviews_yday
        FROM events
        WHERE timestamp >= toStartOfDay(now() - INTERVAL 1 day)
          AND timestamp < toStartOfDay(now())
    """

    all_rows = []
    ts = pd.Timestamp.utcnow().floor("s")
    
    for project_id, domain in project_domain_map.items():
        url = f"{host}/api/projects/{project_id}/query"
        try:
            response = requests.post(url, headers=headers, json={"query": {"kind": "HogQLQuery", "query": query}}, timeout=10)
            response.raise_for_status()
        except requests.RequestException as ex:
            logger.error(f"Failed to fetch PostHog data from {url}: {ex}")
            continue

        data = response.json()
        results = data.get("results") or data.get("data")
        if not results:
            continue

        first = results[0]
        if isinstance(first, dict):
            metrics = {
                "events_yday": first.get("events_yday"),
                "users_yday": first.get("users_yday"), 
                "pageviews_yday": first.get("pageviews_yday")
            }
        else:
            # Handle list response
            metrics = {
                "events_yday": first[0] if len(first) > 0 else None,
                "users_yday": first[1] if len(first) > 1 else None,
                "pageviews_yday": first[2] if len(first) > 2 else None
            }

        for metric_key, value in metrics.items():
            if value is not None:
                all_rows.append({
                    "metric_timestamp": ts,
                    "metric_name": f"ph.{domain}.{metric_key}",
                    "metric_value": float(value)
                })

    df = pd.DataFrame(all_rows)
    return df[["metric_timestamp", "metric_name", "metric_value"]] if not df.empty else df
