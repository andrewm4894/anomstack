import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Credit to: https://stackoverflow.com/a/76580610/1919374
    """

    import pandas as pd
    import requests

    apiBase = "https://query2.finance.yahoo.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"}

    def getCredentials(
        cookieUrl="https://fc.yahoo.com", crumbUrl=apiBase + "/v1/test/getcrumb"
    ):
        cookie = requests.get(cookieUrl, timeout=30).cookies
        crumb = requests.get(
            url=crumbUrl, cookies=cookie, headers=headers, timeout=30
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
            timeout=30,
        )
        quotes = response.json()["quoteResponse"]["result"]
        return quotes

    symbols = [
        "GOOG",   # Alphabet Inc. (Class C)
        "TSLA",   # Tesla, Inc.
        "AAPL",   # Apple Inc.
        "MSFT",   # Microsoft Corporation
        "NVDA",   # NVIDIA Corporation
        "AMZN",   # Amazon.com, Inc.
        "TSM",    # Taiwan Semiconductor Manufacturing Co.
        "META",   # Meta Platforms, Inc.
        "NFLX",   # Netflix, Inc.
        "WMT",    # Walmart Inc.
        "DIS",    # The Walt Disney Company
        "JNJ",    # Johnson & Johnson
        "BRK-B",  # Berkshire Hathaway Inc. (Class B)
        "V",      # Visa Inc.
        "JPM",    # JPMorgan Chase & Co.
        "UNH",    # UnitedHealth Group Inc.
        "XOM",    # Exxon Mobil Corporation
        "PEP",    # PepsiCo, Inc.
        "COST",   # Costco Wholesale Corporation
        "NKE",    # Nike, Inc.
        "BAC",    # Bank of America Corporation
        "AMD",    # Advanced Micro Devices, Inc.
    ]

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


if __name__ == "__main__":
    df = ingest()
    print(df)
