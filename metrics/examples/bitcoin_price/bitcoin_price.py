from dotenv import load_dotenv
import pandas as pd
import requests


def ingest() -> pd.DataFrame:
    """Fetch the current Bitcoin price in USD from the Coindesk API."""
    url = "https://api.coindesk.com/v1/bpi/currentprice.json"
    res = requests.get(url, timeout=10).json()
    price = float(res["bpi"]["USD"]["rate_float"])
    ts = pd.to_datetime(res["time"]["updatedISO"])
    df = pd.DataFrame([["bitcoin_price_usd", price]], columns=["metric_name", "metric_value"])
    df["metric_timestamp"] = ts
    return df


if __name__ == "__main__":
    load_dotenv(override=True)
    pd.set_option("display.max_columns", None)
    print(ingest())
