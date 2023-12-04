import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Ingest TomTom data from the API.
    """

    import os

    import requests

    tomtom_api_key = os.environ["ANOMSTACK_TOMTOM_API_KEY"]

    def make_df(label, data) -> pd.DataFrame:
        current_speed = data["flowSegmentData"]["currentSpeed"]
        current_travel_time = data["flowSegmentData"]["currentTravelTime"]

        metrics = [
            (f"tomtom_{label}_current_speed", current_speed),
            (f"tomtom_{label}_current_travel_time", current_travel_time),
        ]

        df = pd.DataFrame(metrics, columns=["metric_name", "metric_value"])
        df = df.dropna()
        df["metric_timestamp"] = pd.Timestamp.utcnow()
        df = df[["metric_timestamp", "metric_name", "metric_value"]]

        return df

    latlong_list = [
        ("amsterdam", "52.41072,4.84239"),
        ("dublin", "53.3472695,-6.261671"),
        ("london", "51.528607,-0.4312413"),
        ("nyc", "40.69754,-74.0209442"),
    ]

    urls = [
        (
            latlong[0],
            f"https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json?point={latlong[1]}&unit=KMPH&openLr=false&key={tomtom_api_key}",
        )
        for latlong in latlong_list
    ]

    headers = {}

    df = pd.DataFrame()

    for label, url in urls:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        df_metric = make_df(label, data)
        df = pd.concat([df, df_metric])

    return df


if __name__ == "__main__":
    df = ingest()
    print(df)
