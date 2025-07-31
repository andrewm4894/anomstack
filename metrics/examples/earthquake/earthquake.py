def ingest():
    """Summarise earthquake activity from the USGS last day feed."""
    import pandas as pd
    import requests

    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    res = requests.get(url, timeout=10).json()
    mags = [
        f["properties"]["mag"]
        for f in res.get("features", [])
        if f["properties"].get("mag") is not None
    ]
    count = len(mags)
    max_mag = max(mags) if mags else 0
    avg_mag = sum(mags) / count if count else 0
    metrics = [
        ["earthquake_count_last_day", count],
        ["earthquake_max_magnitude_last_day", max_mag],
        ["earthquake_avg_magnitude_last_day", avg_mag],
    ]
    df = pd.DataFrame(metrics, columns=["metric_name", "metric_value"])
    df["metric_timestamp"] = pd.Timestamp.utcnow()
    return df


if __name__ == "__main__":
    from dotenv import load_dotenv
    import pandas as pd

    load_dotenv(override=True)
    pd.set_option("display.max_columns", None)
    print(ingest())
