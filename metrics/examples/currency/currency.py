def ingest():
    """
    Ingest currency conversion data from the currency API for multiple base currencies.
    For each base currency in base_currencies, constructs the URL using the current UTC date and retrieves data.
    Filters the response to include only a subset of target currencies (e.g. USD, GBP, JPY, CHF, AUD, CAD).
    Returns a DataFrame with columns: metric_timestamp, metric_name, and metric_value.
    """
    from datetime import datetime

    from dagster import get_dagster_logger
    import pandas as pd
    import requests

    logger = get_dagster_logger()

    base_currencies = [
        "eur",
        "usd",
        "gbp",
        "jpy",
        "chf",
        "aud",
        "cad",
    ]

    current_date = datetime.now().strftime("%Y-%m-%d")

    currencies_to_include = [
        "usd",
        "gbp",
        "jpy",
        "chf",
        "aud",
        "cad",
        "rub",
        "inr",
        "brl",
        "zar",
        "cny",
        "sek",
        "nzd",
    ]

    all_rows = []

    for base in base_currencies:
        base_url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{current_date}/v1/currencies/{base}.json"
        try:
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch data from {base_url}: {e}")
            continue

        data = response.json()
        response_date = data.get("date", current_date)
        base_data = data.get(base, {})

        for target_currency, rate in base_data.items():
            if target_currency in currencies_to_include:
                currency_pair = f"{base}_{target_currency}"
                try:
                    rate_val = float(rate)
                except (TypeError, ValueError):
                    rate_val = None
                all_rows.append(
                    {
                        "metric_timestamp": response_date,
                        "metric_name": currency_pair,
                        "metric_value": rate_val,
                    }
                )

    df = pd.DataFrame(all_rows, columns=["metric_timestamp", "metric_name", "metric_value"])

    return df
