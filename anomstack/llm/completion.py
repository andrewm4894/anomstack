import json
import openai
import time


def get_completion(prompt: str, model="gpt-4-0613", max_retries=5):
    """
    Get a completion from the OpenAI API.

    Args:
        prompt (str): The prompt to send to the OpenAI API.
        max_retries (int): The maximum number of retries before giving up.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating whether the metric looks anomalous,
        and a string describing the anomaly (if is_anomalous=True, else None).
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
                                    "description": "True if the metric looks anomalous, False otherwise.",
                                },
                                "anomaly_description": {
                                    "type": "string",
                                    "description": "A description of the anomaly, if is_anomalous=True, else None.",
                                },
                            },
                            "required": ["is_anomalous", "anomaly_description"],
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
    anomaly_description = funcs["anomaly_description"]

    return is_anomalous, anomaly_description
