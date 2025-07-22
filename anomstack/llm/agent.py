import pandas as pd
from anomaly_agent import AnomalyAgent


def detect_anomalies(
    df: pd.DataFrame,
    detection_prompt: str | None = None,
    verification_prompt: str | None = None
) -> pd.DataFrame:
    """
    Detect anomalies using the AnomalyAgent.

    Args:
        df (pd.DataFrame): The input DataFrame containing metric data.
        detection_prompt (str, optional): The detection prompt for the AnomalyAgent.
            If None, uses anomaly-agent's default.
        verification_prompt (str, optional): The verification prompt for the AnomalyAgent.
            If None, uses anomaly-agent's default.

    Returns:
        pd.DataFrame: A DataFrame containing the detected anomalies.
    """
    # Build AnomalyAgent kwargs, only including non-None values
    agent_kwargs = {}
    if detection_prompt is not None:
        agent_kwargs["detection_prompt"] = detection_prompt
    if verification_prompt is not None:
        agent_kwargs["verification_prompt"] = verification_prompt

    anomaly_agent = AnomalyAgent(**agent_kwargs)
    anomalies = anomaly_agent.detect_anomalies(df, timestamp_col="metric_timestamp")
    df_anomalies = anomaly_agent.get_anomalies_df(anomalies)

    return df_anomalies
