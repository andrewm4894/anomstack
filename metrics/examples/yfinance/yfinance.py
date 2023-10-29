import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Credit to: https://stackoverflow.com/a/76580610/1919374 
    """

    import requests
    import pandas as pd

    
    apiBase = "https://query2.finance.yahoo.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"}
    
    
    def getCredentials(
        cookieUrl="https://fc.yahoo.com", crumbUrl=apiBase + "/v1/test/getcrumb"
    ):
        cookie = requests.get(cookieUrl, timeout=10).cookies
        crumb = requests.get(
            url=crumbUrl, cookies=cookie, headers=headers, timeout=10
        ).text
        return {"cookie": cookie, "crumb": crumb}

    def quote(symbols, credentials):
        url = apiBase + "/v7/finance/quote"
        params = {"symbols": ",".join(symbols), "crumb": credentials["crumb"]}
        response = requests.get(
            url,
            params=params,
            cookies=credentials["cookie"],
            headers=headers,
            timeout=10,
        )
        quotes = response.json()["quoteResponse"]["result"]
        return quotes


    symbols = ["GOOG", "TSLA", "AAPL", "MSFT"]

    credentials = getCredentials()
    quotes = quote(symbols, credentials)

    if quotes:
        prices = []
        metric_names = []
        for quote in quotes:
            prices.append(quote["regularMarketPrice"])
            metric_names.append(f"yf_{quote['symbol'].lower()}_price")

    df = pd.DataFrame(
        {
            "metric_name": metric_names,
            "metric_value": prices,
        }
    )
    df["metric_timestamp"] = pd.Timestamp.utcnow()

    return df
