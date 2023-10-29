import pandas as pd


def ingest() -> pd.DataFrame:
    """ """

    import requests
    import time
    import pandas as pd

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }

    tickers = ["AAPL", "MSFT", "GOOG", "NVDA"]

    prices = []
    metric_names = []

    for ticker in tickers:
        time.sleep(1)
        url = f"https://query2.finance.yahoo.com/v6/finance/quoteSummary/{ticker}?modules=financialData&ssl=true"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = data["quoteSummary"]["result"][0]["financialData"]["currentPrice"]["raw"]
            prices.append(price)
            metric_names.append(f"yf_{ticker.lower()}_price")

    df = pd.DataFrame(
        {
            "metric_name": metric_names,
            "metric_value": prices,
        }
    )
    df["metric_timestamp"] = pd.Timestamp.utcnow()

    return df
