def ingest():
    """
    Ingest data from the Coindesk API.
    Retrieves tick data for BTC-USD and ETH-USD and returns a DataFrame with columns:
    metric_timestamp, metric_name, metric_value.
    The timestamp is derived from VALUE_LAST_UPDATE_TS, aggregated to the second, and duplicates are removed.
    """
    import pandas as pd
    from dagster import get_dagster_logger
    import requests

    logger = get_dagster_logger()

    url = "https://data-api.coindesk.com/index/cc/v1/latest/tick"
    params = {"market": "cadli", "instruments": "BTC-USD,ETH-USD", "apply_mapping": "true"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from {url}: {e}")
        return pd.DataFrame(columns=["metric_timestamp", "metric_name", "metric_value"])

    data = response.json()
    if data.get("Err"):
        logger.error(f"API returned an error: {data.get('Err')}")
        return pd.DataFrame(columns=["metric_timestamp", "metric_name", "metric_value"])

    all_rows = []
    # Process each instrument's data from the API response.
    instruments_data = data.get("Data", {})
    for instrument, instrument_data in instruments_data.items():
        # Use VALUE_LAST_UPDATE_TS as the base timestamp; if missing, use current UTC time.
        ts_value = instrument_data.get("VALUE_LAST_UPDATE_TS")
        try:
            ts = (
                pd.to_datetime(float(ts_value), unit="s").floor("S")
                if ts_value is not None
                else pd.Timestamp.utcnow().floor("S")
            )
        except Exception as ex:
            logger.error(f"Error converting timestamp for instrument {instrument}: {ex}")
            ts = pd.Timestamp.utcnow().floor("S")

        # Define keys to skip (non-numeric or meta data).
        skip_keys = {"TYPE", "MARKET", "INSTRUMENT", "VALUE_FLAG"}
        for key, value in instrument_data.items():
            if key in skip_keys:
                continue
            try:
                metric_value = float(value)
            except (TypeError, ValueError):
                continue  # Skip non-numeric values

            # Build a metric name in the format: coindesk.<instrument>.<key>
            metric_name = f"coindesk.{instrument}.{key}"
            all_rows.append(
                {"metric_timestamp": ts, "metric_name": metric_name, "metric_value": metric_value}
            )

    df = pd.DataFrame(all_rows)

    # Filter out metrics that are not current hour.
    df = df[df["metric_name"].str.contains("CURRENT_HOUR")]

    # Remove duplicates based on the second-level timestamp and metric name.
    df = df.drop_duplicates(subset=["metric_timestamp", "metric_name"])
    logger.debug(f"df:\n{df}")

    # Ensure the final column order.
    df = df[["metric_timestamp", "metric_name", "metric_value"]]
    return df
