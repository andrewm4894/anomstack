import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Ingest data from Netdata API.
    """

    import requests
    import pandas as pd
    from dagster import get_dagster_logger

    logger = get_dagster_logger()

    # [(host, chart, after, before)]
    inputs = [
        ("london.my-netdata.io", "system.net", "-600", "0"),
        ("london.my-netdata.io", "system.cpu", "-600", "0"),
        ("london.my-netdata.io", "system.io", "-600", "0"),
        ("london.my-netdata.io", "system.ram", "-600", "0"),
    ]

    urls = [
        f"https://{host}/api/v1/data?chart={chart}&after={after}&before={before}&points=1&format=csv"
        for host, chart, after, before in inputs
    ]
    df = pd.DataFrame()
    for url, (host, chart, _, _) in zip(urls, inputs):
        res = requests.get(url)
        data = res.text.split("\r\n")
        cols = data[0].split(",")
        values = data[1].split(",")
        df_tmp = pd.DataFrame(data=[values], columns=cols)
        df_tmp["host"] = host
        df_tmp["chart"] = chart
        df_tmp = df_tmp.melt(
            id_vars=["time", "host", "chart"],
            var_name="metric_name",
            value_name="metric_value",
        )
        df_tmp = df_tmp.rename(columns={"time": "metric_timestamp"})
        df = pd.concat([df, df_tmp])

    # add host and chart prefix to metric name
    df["metric_name"] = df["host"] + "." + df["chart"] + "." + df["metric_name"]

    # add timestamp
    df["metric_timestamp"] = pd.Timestamp.utcnow()

    # clean metric_name
    df["metric_name"] = df["metric_name"].str.replace("my-netdata.io", "", regex=False)
    df["metric_name"] = df["metric_name"].str.replace(".", "_", regex=False)
    df["metric_name"] = df["metric_name"].str.replace("-", "_", regex=False)

    df = df[["metric_timestamp", "metric_name", "metric_value"]]

    logger.debug(f'df:\n{df}')

    df["metric_value"] = df["metric_value"].astype(float)

    return df
