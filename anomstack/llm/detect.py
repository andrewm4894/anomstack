"""
Helper functions for interacting with LLM providers (OpenAI, Anthropic) to detect anomalies.
"""

import os
from typing import Any, Dict, List

from anomstack.llm.anthropic import detect_anomalies_anthropic
from anomstack.llm.openai import detect_anomalies_openai

DEFAULT_LLM_PLATFORM = "openai"


def detect_anomalies(prompt: str, max_retries: int = 5) -> List[Dict[str, Any]]:
    """
    Dispatch to the appropriate LLM platform (OpenAI or Anthropic)
    based on the ANOMSTACK_LLM_PLATFORM environment variable.
    """
    platform = os.getenv("ANOMSTACK_LLM_PLATFORM", DEFAULT_LLM_PLATFORM).lower()
    if platform == "anthropic":
        return detect_anomalies_anthropic(prompt, max_retries)
    else:
        # Default to OpenAI
        return detect_anomalies_openai(prompt, max_retries)
