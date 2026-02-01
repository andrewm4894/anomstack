from anomaly_agent import AnomalyAgent
import pandas as pd


def detect_anomalies(
    df: pd.DataFrame,
    detection_prompt: str | None = None,
    verification_prompt: str | None = None,
    include_plot: bool = False,
    model_name: str = "gpt-5-mini",
    posthog_metadata: dict | None = None,
) -> pd.DataFrame:
    """
    Detect anomalies using the AnomalyAgent.

    Args:
        df (pd.DataFrame): The input DataFrame containing metric data.
        detection_prompt (str, optional): The detection prompt for the AnomalyAgent.
            If None, uses anomaly-agent's default.
        verification_prompt (str, optional): The verification prompt for the AnomalyAgent.
            If None, uses anomaly-agent's default.
        include_plot (bool, optional): If True, include a plot image in the LLM prompt
            for multimodal analysis. Defaults to False.
        model_name (str, optional): The OpenAI model to use for anomaly detection.
            Defaults to "gpt-4o-mini".
        posthog_metadata (dict, optional): Custom metadata to include in PostHog traces.
            Useful for linking LLM traces to metric batches and Dagster runs.

    Returns:
        pd.DataFrame: A DataFrame containing the detected anomalies.
    """
    # Build AnomalyAgent kwargs, only including non-None values
    agent_kwargs = {"include_plot": include_plot, "model_name": model_name}
    if detection_prompt is not None:
        agent_kwargs["detection_prompt"] = detection_prompt
    if verification_prompt is not None:
        agent_kwargs["verification_prompt"] = verification_prompt
    if posthog_metadata is not None:
        agent_kwargs["posthog_metadata"] = posthog_metadata

    anomaly_agent = AnomalyAgent(**agent_kwargs)
    anomalies = anomaly_agent.detect_anomalies(df, timestamp_col="metric_timestamp")
    df_anomalies = anomaly_agent.get_anomalies_df(anomalies)

    return df_anomalies
