def make_prompt(df, llmalert_recent_n) -> str:
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

    I am interested in finding anomalies in the time series data for the metric.

    I am interested in looking at the last {llmalert_recent_n} observations and if it looks like the more recent data may be anomalous or if it looks not all that much different from the rest of the data.
    
    Here are some questions to think about:
    
    - Is there anything unusual about the last {llmalert_recent_n} values of the metric_value column in the df DataFrame?
    - Are there any anomalies or outliers in the recent {llmalert_recent_n} observations of metric_value in df?
    - Can you identify any patterns or trends in the last {llmalert_recent_n} values of metric_value in df that could be indicative of an anomaly?
    - How does the distribution of the last {llmalert_recent_n} values of metric_value in df compare to the distribution of the entire dataset?
    - Are there any changes in the mean, median, or standard deviation of metric_value in the last {llmalert_recent_n} observations that could be indicative of an anomaly?
    - Is there a sudden increase or decrease in metric_value in the last {llmalert_recent_n} observations?
    - Is there a change in the slope of the metric_value trend line in the last {llmalert_recent_n} observations?
    - Are there any spikes or dips in metric_value in the last {llmalert_recent_n} observations?
    - Do the last {llmalert_recent_n} observations fall outside of the normal range of metric_value?
    - Are there any patterns in the timing of the anomalies in the last {llmalert_recent_n} observations?

    Here is the data:

    {df.to_string(max_rows=len(df), max_cols=(len(df.columns)))}

    I need a yes or no answer as to if you think the recent data looks anomalous or not.

    Please also provide a description on why the metric looks anomalous if you think it does.
    
    Also think about and provide a confidence level on how confident ('high', 'medium', 'low') you are that the metric is anomalous.
    """

    return prompt
