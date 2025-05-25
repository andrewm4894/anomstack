import pandas as pd

from anomaly_agent import AnomalyAgent


def detect_anomalies(df: pd.DataFrame, system_prompt: str) -> pd.DataFrame:
    """
    Detect anomalies using the AnomalyAgent.

    Args:
        df (pd.DataFrame): The input DataFrame containing metric data.
        system_prompt (str): The system prompt for the AnomalyAgent.

    Returns:
        pd.DataFrame: A DataFrame containing the detected anomalies.
    """
    anomaly_agent = AnomalyAgent(system_prompt=system_prompt)
    anomalies = anomaly_agent.detect_anomalies(df, timestamp_col="metric_timestamp")
    df_anomalies = anomaly_agent.get_anomalies_df(anomalies)

    return df_anomalies
