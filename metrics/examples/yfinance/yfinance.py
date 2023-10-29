def ingest() -> pd.DataFrame:
    """
    """

    import pandas as pd
    import yfinance as yf
    import requests_cache

    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'

    prices = []
    tickers = ['AAPL','MSFT','GOOG','NVDA']
    for ticker in tickers:
        stock = yf.Ticker(ticker, session=session)
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
