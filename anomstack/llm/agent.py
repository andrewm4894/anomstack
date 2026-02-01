import os
import random

from anomaly_agent import AnomalyAgent
import pandas as pd

# Default models for random selection
DEFAULT_MODELS = [
    "gpt-4o-mini",
]

# Provider base URLs
PROVIDER_BASE_URLS = {
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": None,  # Use default
}


def get_base_url() -> str | None:
    """Get the base URL for the LLM provider.

    Checks ANOMSTACK_LLM_PLATFORM first, then falls back to OPENROUTER_BASE_URL.
    """
    platform = os.getenv("ANOMSTACK_LLM_PLATFORM", "").lower()
    if platform in PROVIDER_BASE_URLS:
        return PROVIDER_BASE_URLS[platform]
    # Fall back to explicit base URL env vars
    return os.getenv("OPENROUTER_BASE_URL") or os.getenv("OPENAI_BASE_URL")


def get_model_list() -> list[str]:
    """Get list of models for random selection.

    Returns models from ANOMSTACK_LLMALERT_MODELS env var (comma-separated),
    or DEFAULT_MODELS if not set.
    """
    models_env = os.getenv("ANOMSTACK_LLMALERT_MODELS", "")
    if models_env:
        return [m.strip() for m in models_env.split(",") if m.strip()]
    return DEFAULT_MODELS


def select_model(model_name: str | None = None) -> str:
    """Select a model for LLM alert.

    Args:
        model_name: Specific model to use. If None or "random", randomly
            selects from the configured model list.

    Returns:
        The selected model name.
    """
    if model_name is None or model_name.lower() == "random":
        models = get_model_list()
        return random.choice(models)
    return model_name


def detect_anomalies(
    df: pd.DataFrame,
    detection_prompt: str | None = None,
    verification_prompt: str | None = None,
    include_plot: bool = False,
    model_name: str | None = None,
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
        model_name (str, optional): The model to use for anomaly detection.
            If None or "random", randomly selects from ANOMSTACK_LLMALERT_MODELS.
            Supports OpenRouter format (e.g., "anthropic/claude-3.5-sonnet").
        posthog_metadata (dict, optional): Custom metadata to include in PostHog traces.
            Useful for linking LLM traces to metric batches and Dagster runs.

    Returns:
        pd.DataFrame: A DataFrame containing the detected anomalies.
    """
    # Select model (random if not specified)
    selected_model = select_model(model_name)

    # Add selected model to PostHog metadata for tracking/evals
    metadata = posthog_metadata.copy() if posthog_metadata else {}
    metadata["llmalert_model"] = selected_model

    # Build AnomalyAgent kwargs
    agent_kwargs = {
        "include_plot": include_plot,
        "model_name": selected_model,
        "posthog_metadata": metadata,
    }

    # Set base_url for OpenRouter or other providers
    base_url = get_base_url()
    if base_url:
        agent_kwargs["base_url"] = base_url

    if detection_prompt is not None:
        agent_kwargs["detection_prompt"] = detection_prompt
    if verification_prompt is not None:
        agent_kwargs["verification_prompt"] = verification_prompt

    anomaly_agent = AnomalyAgent(**agent_kwargs)
    anomalies = anomaly_agent.detect_anomalies(df, timestamp_col="metric_timestamp")
    df_anomalies = anomaly_agent.get_anomalies_df(anomalies)

    return df_anomalies
