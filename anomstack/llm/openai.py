import json
import os
import time
from typing import Any, Dict, List

import openai
from dagster import get_dagster_logger
from pydantic import ValidationError

from anomstack.llm.models import DetectAnomaliesResponse, detect_anomalies_schema

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def detect_anomalies_openai(prompt: str, max_retries: int = 5) -> List[Dict[str, Any]]:
    """
    Detect anomalies using the OpenAI API.

    Args:
        prompt (str): The prompt or data to analyze for anomalies.
        max_retries (int, optional): The maximum number of retries before giving up.

    Returns:
        List[Dict[str, Any]]: A list of anomalies, each with 'anomaly_timestamp' and 'anomaly_explanation'.
    """
    api_key = os.getenv("ANOMSTACK_OPENAI_KEY")
    if not api_key:
        raise EnvironmentError("ANOMSTACK_OPENAI_KEY is not set.")

    client = openai.OpenAI(api_key=api_key)
    openai_model = os.getenv("ANOMSTACK_OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

    logger = get_dagster_logger()
    logger.debug(f"Using OpenAI model: {openai_model}")

    messages = [{"role": "user", "content": prompt}]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "detect_anomalies",
                "parameters": detect_anomalies_schema,
            },
        }
    ]

    retries = 0
    completion = None
    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model=openai_model,
                messages=messages,
                tools=tools,
            )
            break
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit reached. Waiting for {e.retry_after} seconds...")
            time.sleep(e.retry_after)
            retries += 1
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    if completion is None:
        raise ValueError("Maximum number of retries reached. Aborting.")

    response_message = completion.choices[0].message
    tool_call = response_message.tool_calls[0]

    try:
        function_args = json.loads(tool_call.function.arguments)
        response_data = DetectAnomaliesResponse(**function_args)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        raise ValueError("Invalid JSON format in tool call arguments.")
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValueError("Response does not match the expected schema.")

    anomalies = [anomaly.dict() for anomaly in response_data.anomalies]
    return anomalies
