import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Ingest data from Netdata API.
    """

    import pandas as pd
    import requests
    from dagster import get_dagster_logger

    logger = get_dagster_logger()

    # [(host, chart, after, before)]
    inputs = [
        (
            "london.my-netdata.io",
            "httpcheck_San_Francisco_Demo_Site_(CloudFlare).response_time",
            "-120",
            "0",
        ),
        (
            "london.my-netdata.io",
            "httpcheck_Frankfurt_Demo_Site_(CloudFlare).response_time",
            "-120",
            "0",
        ),
        (
            "london.my-netdata.io",
            "httpcheck_Toronto_Demo_Site_(CloudFlare).response_time",
            "-120",
            "0",
        ),
        (
            "london.my-netdata.io",
            "httpcheck_New_York_Demo_Site_(CloudFlare).response_time",
            "-120",
            "0",
        ),
        (
            "london.my-netdata.io",
            "httpcheck_Bangalore_Demo_Site_(CloudFlare).response_time",
            "-120",
            "0",
        ),
        (
            "london.my-netdata.io",
            "httpcheck_Singapore_Demo_Site_(CloudFlare).response_time",
            "-120",
            "0",
        ),
        (
            "sanfrancisco.my-netdata.io",
            "httpcheck_London_Demo_Site_(CloudFlare).response_time",
            "-120",
            "0",
        ),
    ]

    urls = [
        f"https://{host}/api/v1/data?chart={chart}&after={after}&before={before}&points=1&format=csv"
        for host, chart, after, before in inputs
    ]
    df = pd.DataFrame()
    for url, (host, chart, _, _) in zip(urls, inputs):
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            continue
        data = res.text.split("\r\n")
        cols = data[0].split(",")
        cols[0] = "metric_timestamp"
        values = data[1].split(",")
        df_tmp = pd.DataFrame(data=[values], columns=cols)
        print(df_tmp)
        df_tmp["host"] = host
        df_tmp["chart"] = chart
        df_tmp = df_tmp.melt(
            id_vars=["metric_timestamp", "host", "chart"],
            var_name="metric_name",
            value_name="metric_value",
        )
        df = pd.concat([df, df_tmp])

    # add host and chart prefix to metric name
    df["metric_name"] = df["host"] + "." + df["chart"] + "." + df["metric_name"]

    # add timestamp
    df["metric_timestamp"] = pd.Timestamp.utcnow()

    # clean metric_name
    df["metric_name"] = df["metric_name"].str.replace("my-netdata.io", "", regex=False)
    df["metric_name"] = df["metric_name"].str.replace(".", "_", regex=False)
    df["metric_name"] = df["metric_name"].str.replace("-", "_", regex=False)
    df["metric_name"] = df["metric_name"].str.replace("(", "_", regex=False)
    df["metric_name"] = df["metric_name"].str.replace(")", "_", regex=False)
    df["metric_name"] = df["metric_name"].str.replace("__", "_", regex=False)
    df["metric_name"] = df["metric_name"].str.replace("CloudFlare", "cf", regex=False)
    df["metric_name"] = df["metric_name"].str.lower()

    df = df[["metric_timestamp", "metric_name", "metric_value"]]

    logger.debug(f"df:\n{df}")

    df["metric_value"] = df["metric_value"].astype(float)

    return df


if __name__ == "__main__":
    df = ingest()
    print(df)
