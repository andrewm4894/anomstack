from dotenv import load_dotenv
import pandas as pd
import requests


def ingest() -> pd.DataFrame:
    """Get the current ISS location from the Open Notify API."""
    url = "http://api.open-notify.org/iss-now.json"
    res = requests.get(url, timeout=10).json()
    ts = pd.to_datetime(int(res["timestamp"]), unit="s")
    pos = res["iss_position"]
    metrics = [
        ["iss_latitude", float(pos["latitude"])],
        ["iss_longitude", float(pos["longitude"])],
    ]
    df = pd.DataFrame(metrics, columns=["metric_name", "metric_value"])
    df["metric_timestamp"] = ts
    return df


if __name__ == "__main__":
    load_dotenv(override=True)
    pd.set_option("display.max_columns", None)
    print(ingest())
