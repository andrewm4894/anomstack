
import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Ingest weather data from open-meteo.com.
    """

    import requests

    # Define cities and their coordinates
    cities = [
        ("dublin", 53.3441, -6.2675),
        ("athens", 37.9792, 23.7166),
        ("london", 51.5002, -0.1262),
        ("berlin", 52.5235, 13.4115),
        ("paris", 48.8567, 2.3510),
        ("madrid", 40.4167, -3.7033),
        ("new_york", 40.7128, -74.0060),
        ("los_angeles", 34.0522, -118.2437),
        ("sydney", -33.8688, 151.2153),
        ("tokyo", 35.6812, 139.7671),
        ("beijing", 39.9087, 116.3975),
        ("cape_town", -33.9249, 18.4241),
    ]

    # Define metrics to fetch
    metrics = [
        "temperature_2m",
        "precipitation",
        "windspeed_10m",
        "cloudcover",
        "uv_index",
        "visibility",
        "precipitation_probability",
        "uv_index"
    ]

    data = {}
    for city, lat, lng in cities:
        response = requests.get(
            url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current={','.join(metrics)}",
            timeout=10,
        ).json()["current"]

        for metric in metrics:
            data[f"{city}_{metric}"] = response[metric]

    df = pd.DataFrame.from_dict(data, columns=["metric_value"], orient="index")
    df["metric_timestamp"] = pd.Timestamp.utcnow()
    df["metric_name"] = "temp_" + df.index
    df = df[["metric_timestamp", "metric_name", "metric_value"]]

    return df
