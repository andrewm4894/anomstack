def ingest():
    """Get the current ISS location from the Open Notify API."""
    import pandas as pd
    import requests

    url = "http://api.open-notify.org/iss-now.json"
    res = requests.get(url, timeout=10).json()
    ts = pd.to_datetime(int(res["timestamp"]), unit="s")
    pos = res["iss_position"]
    
    lat = float(pos["latitude"])
    lon = float(pos["longitude"])
    
    metrics = [
        ["iss_latitude", lat],
        ["iss_longitude", lon],
        ["latlong_avg", (lat + lon) / 2],
        ["latlong_sum", lat + lon],
        ["latlong_diff", lat - lon],
    ]
    df = pd.DataFrame(metrics, columns=["metric_name", "metric_value"])
    df["metric_timestamp"] = ts
    return df


if __name__ == "__main__":
    from dotenv import load_dotenv
    import pandas as pd

    load_dotenv(override=True)
    pd.set_option("display.max_columns", None)
    print(ingest())
