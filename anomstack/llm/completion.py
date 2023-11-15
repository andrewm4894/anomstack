import json
import time
import os

from openai import OpenAI
import openai


def get_completion(prompt: str, max_retries=5):
    """
    Get a completion from the OpenAI API.

    Args:
        prompt (str): The prompt to send to the OpenAI API.
        model (str, optional): The model to use for the completion. Defaults to "gpt-3.5-turbo".
        max_retries (int, optional): The maximum number of retries before giving up.

    Returns:
        Tuple[bool, str, str]: A tuple containing a boolean indicating whether the metric looks anomalous,
        a string describing the anomaly (if is_anomalous=True, else None) and a confidence level.
    """

    client = OpenAI(api_key=os.getenv("ANOMSTACK_OPENAI_KEY"))
    openai_model = os.getenv("ANOMSTACK_OPENAI_MODEL", "gpt-3.5-turbo")

    messages = [{"role": "user", "content": prompt}]

    retries = 0
    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model=openai_model,
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "trigger_anomaly_alert",
                            "description": "If the metric looks anomalous then flag it as anomalous.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "is_anomalous": {
                                        "type": "boolean",
                                        "description": "True if the recent metric values looks anomalous, False otherwise.",
                                    },
                                    "decision_reasoning": {
                                        "type": "string",
                                        "description": "A detailed description, referencing observations by their index number or value, on why or why not the metric looks anomalous.",
                                    },
                                    "decision_confidence_level": {
                                        "type": "string",
                                        "enum": ["high", "medium", "low"],
                                        "description": "Confidence level in the `is_anomalous` flag. 'high' if very confident in the anomaly decision, 'medium' if somewhat confident, 'low' if not confident.",
                                    },
                                },
                                "required": [
                                    "is_anomalous",
                                    "decision_reasoning",
                                    "decision_confidence_level",
                                ],
                            },
                        },
                    }
                ],
                tool_choice={
                    "type": "function",
                    "function": {"name": "trigger_anomaly_alert"},
                },
            )
            break
        except openai.RateLimitError as e:
            print(f"Rate limit reached. Waiting for {e.retry_after} seconds...")
            time.sleep(e.retry_after)
            retries += 1

    if retries == max_retries:
        raise ValueError("Maximum number of retries reached. Aborting.")

    response_message = completion.choices[0].message
    tool_call = response_message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    is_anomalous = function_args.get("is_anomalous")
    decision_reasoning = function_args.get("decision_reasoning")
    decision_confidence_level = function_args.get("decision_confidence_level")

    return is_anomalous, decision_reasoning, decision_confidence_level
