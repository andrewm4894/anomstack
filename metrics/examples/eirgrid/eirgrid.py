import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Ingest EirGrid data from the API.
    """

    from datetime import date

    import requests

    def make_df(data) -> pd.DataFrame:
        if "Rows" not in data:
            print("No data found")
            print(data)
            return pd.DataFrame()

        df = pd.DataFrame(data["Rows"])
        df = df[["EffectiveTime", "FieldName", "Value"]]
        df.columns = ["metric_timestamp", "metric_name", "metric_value"]
        df = df.dropna()
        df["metric_timestamp"] = pd.to_datetime(df["metric_timestamp"])
        df = df.sort_values(by="metric_timestamp", ascending=False).head(1)
        df["metric_name"] = df["metric_name"].str.lower()
        df["metric_name"] = "eirgrid_" + df["metric_name"]
        df = df[["metric_timestamp", "metric_name", "metric_value"]]

        return df

    today = date.today().strftime("%d-%b-%Y")

    area_list = ["demandactual", "generationactual", "windactual", "frequency"]

    urls = [
        f"https://www.smartgriddashboard.com/DashboardService.svc/data?area={area}&region=ALL&datefrom={today}+00%3A00&dateto={today}+23%3A59"
        for area in area_list
    ]

    headers = {}

    df = pd.DataFrame()

    for url in urls:
        response = requests.get(url, headers=headers)
        data = response.json()
        df_metric = make_df(data)
        df = pd.concat([df, df_metric])

    return df


if __name__ == "__main__":
    df = ingest()
    print(df.head())
