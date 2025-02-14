import pandas as pd

from anomaly_agent import AnomalyAgent


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect anomalies using the AnomalyAgent.

    Args:
        df (pd.DataFrame): The input DataFrame containing metric data.

    Returns:
        pd.DataFrame: A DataFrame containing the detected anomalies.
    """
    anomaly_agent = AnomalyAgent()
    anomalies = anomaly_agent.detect_anomalies(df, timestamp_col="metric_timestamp")
    df_anomalies_long = anomaly_agent.get_anomalies_df(anomalies)

    return df_anomalies_long
