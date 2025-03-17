import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Ingest weather data from open-meteo.com.
    """

    import requests

    data = {
        city: requests.get(
            url=f"://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m",
            timeout=10,
        ).json()["current"]["temperature_2m"]
        for (city, lat, lng) in [
            ("dublin", 53.3441, -6.2675),
            ("athens", 37.9792, 23.7166),
            ("london", 51.5002, -0.1262),
            ("berlin", 52.5235, 13.4115),
            ("paris", 48.8567, 2.3510),
        ]
    }

    df = pd.DataFrame.from_dict(data, columns=["metric_value"], orient="index")
    df["metric_timestamp"] = pd.Timestamp.utcnow()
    df["metric_name"] = "temp_" + df.index
    df = df[["metric_timestamp", "metric_name", "metric_value"]]

    return df
