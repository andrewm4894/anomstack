import pandas as pd


def ingest() -> pd.DataFrame:
    """
    Ingest EirGrid data from the API.
    """

    from datetime import date
    import requests

    today = date.today().strftime("%d-%b-%Y")

    url = f'https://www.smartgriddashboard.com/DashboardService.svc/data?area=demandactual&region=ALL&datefrom={today}+00%3A00&dateto={today}+23%3A59'

    headers = {}
    
    response = requests.get(url, headers=headers)

    data = response.json()

    df = pd.DataFrame(data['Rows'])
    df = df[df['Region'] == 'ALL']
    df = df[df['FieldName'] == 'SYSTEM_DEMAND']
    df = df[['EffectiveTime', 'FieldName', 'Value']]
    df.columns = ['metric_timestamp', 'metric_name', 'metric_value']
    df = df.dropna()
    df['metric_timestamp'] = pd.to_datetime(df['metric_timestamp'])
    df = df.sort_values(by='metric_timestamp', ascending=False).head(1)
    df['metric_name'] = df['metric_name'].str.lower()
    df['metric_name'] = 'eirgrid_' + df['metric_name']
    df = df[["metric_timestamp", "metric_name", "metric_value"]]

    return df


if __name__ == "__main__":
    df = ingest()
    print(df.head())
