def make_prompt(df, llmalert_recent_n, metric_name) -> str:
    """
    Generates a prompt for the user to check if there is an anomaly in a time series data.

    Args:
        df (pandas.DataFrame): The time series data to check for anomalies.
        llmalert_recent_n (int): The number of most recent observations to consider.
        metric_name (str): The name of the metric being analyzed.

    Returns:
        str: A prompt for the user to check if there is an anomaly in the time series data.
    """

    prompt = f"""
    Can you help me check if there is an anomaly in this time series data?

    I am interested in finding anomalies in the time series data for metric `{metric_name}`.

    I am interested in looking at the last {llmalert_recent_n} observations and if it looks like the more recent data may be anomalous or if it looks not all that much different from the rest of the data.

    Here is the data:

    {df.to_string(max_rows=len(df), max_cols=(len(df.columns)))}

    I need a yes or no answer as to if you think the recent data looks anomalous or not.

    Please also provide a description on why the metric looks anomalous if you think it does.
    """

    return prompt
