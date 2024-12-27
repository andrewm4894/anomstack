import json
import os
import time
from typing import Any, Dict, List

import anthropic

from dagster import get_dagster_logger
from pydantic import ValidationError
from anomstack.llm.models import DetectAnomaliesResponse, detect_anomalies_schema


DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"


def detect_anomalies_anthropic(prompt: str, max_retries: int = 5) -> List[Dict[str, Any]]:
    """
    Detect anomalies using Anthropic's Messages API.

    Args:
        prompt (str): The prompt or data to analyze for anomalies.
        max_retries (int, optional): The maximum number of retries before giving up.

    Returns:
        List[Dict[str, Any]]: A list of anomalies, each with 'anomaly_timestamp' and 'anomaly_explanation'.
    """
    logger = get_dagster_logger()

    api_key = os.getenv("ANOMSTACK_ANTHROPIC_KEY")
    if not api_key:
        raise EnvironmentError("ANOMSTACK_ANTHROPIC_KEY is not set.")

    anthropic_model = os.getenv("ANOMSTACK_ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    logger.debug(f"Using Anthropic model: {anthropic_model}")

    client = anthropic.Anthropic(api_key=api_key)

    messages = [
        {
            "role": "user",
            "content": prompt,
        },
    ]

    tools = [
        {
            "name": "detect_anomalies",
            "description": "Detect anomalies from user data",
            "input_schema": detect_anomalies_schema,
        }
    ]

    retries = 0
    last_exception = None

    while retries < max_retries:
        try:
            response = client.messages.create(
                model=anthropic_model,
                max_tokens=1024,
                messages=messages,
                tools=tools,
                tool_choice = {"type": "tool", "name": "detect_anomalies"},
            )

            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "detect_anomalies":
                        # check if input is list of anomalies
                        if 'anomalies' in block.input and isinstance(block.input['anomalies'], list):
                            if len(block.input['anomalies']) > 0:
                                logger.debug(f"Anomalies detected: {block.input}")
                                anomalies_response = DetectAnomaliesResponse(**block.input)
                                return [anomaly.dict() for anomaly in anomalies_response.anomalies]

        except anthropic.APIError as e:
            logger.warning(f"Anthropic API error: {e}. Retrying...")
            last_exception = e
            retries += 1
            time.sleep(2)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Error parsing or validating JSON from Anthropic: {e}")
            raise ValueError("Response does not match the expected JSON schema.")

    error_msg = (
        f"Failed to get a valid response from Anthropic after {max_retries} retries. "
        f"Last exception: {last_exception}"
    )
    logger.error(error_msg)
    raise ValueError(error_msg)
