import json
import time

import openai


def get_completion(prompt: str, model="gpt-3.5-turbo", max_retries=5):
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

    messages = [{"role": "user", "content": prompt}]

    retries = 0
    while retries < max_retries:
        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                functions=[
                    {
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
                    }
                ],
                function_call={"name": "trigger_anomaly_alert"},
            )
            break
        except openai.error.RateLimitError as e:
            print(f"Rate limit reached. Waiting for {e.retry_after} seconds...")
            time.sleep(e.retry_after)
            retries += 1

    if retries == max_retries:
        raise ValueError("Maximum number of retries reached. Aborting.")

    reply_content = completion.choices[0]

    funcs = reply_content["message"].to_dict()["function_call"]["arguments"]
    funcs = json.loads(funcs)
    is_anomalous = funcs["is_anomalous"]
    decision_reasoning = funcs["decision_reasoning"]
    decision_confidence_level = funcs["decision_confidence_level"]

    return is_anomalous, decision_reasoning, decision_confidence_level
