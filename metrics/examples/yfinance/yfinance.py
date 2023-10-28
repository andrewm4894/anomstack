def ingest() -> pd.DataFrame:
    """
    """

    import pandas as pd
    import yfinance as yf

    prices = []
    tickers = ['AAPL','MSFT','GOOG','NVDA']
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        latest_price = stock.info["currentPrice"]
        prices.append(latest_price)

    df = pd.DataFrame(
        {
            "metric_name": [f'yf_{t.lower()}_price' for t in tickers],
            "metric_value": prices,
        }
    )
    df['metric_timestamp'] = pd.Timestamp.utcnow()

    return df
