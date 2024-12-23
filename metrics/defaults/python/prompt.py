import pandas as pd

def make_prompt(df: pd.DataFrame, max_rows: int = 1000) -> str:
    """
    Generates a prompt for detecting anomalies in time series data.

    Args:
        df (pandas.DataFrame): The time series data to analyze.

    Returns:
        str: A prompt tailored for anomaly detection using the OpenAI API.
    """
    # Convert the DataFrame to a string table for better readability
    text_representation = df.tail(max_rows).to_string(index=False)

    # Simplified and adapted prompt
    prompt = f"""
    Analyze the following time series data and identify any anomalies in the data.

    **Instructions:**
    - Identify if there are any anomalies or unusual patterns.
    - For each detected anomaly, provide the timestamp and a detailed explanation.

    **Data Details:**
    - The `metric_value` column represents the raw metric values.
    - The `metric_timestamp` column represents the timestamp of each metric value.

    **Expected Output:**
    - A list of anomalies, each containing:
        - `anomaly_timestamp`: The timestamp where the anomaly was detected.
        - `anomaly_explanation`: A brief explanation of why this point is considered anomalous.

    **Data:**

    {text_representation}
    """

    return prompt
