def make_prompt(df, llmalert_recent_n) -> str:
    """
    Generates a prompt for the user to check if there is an anomaly in a time series data.

    Args:
        df (pandas.DataFrame): The time series data to check for anomalies.
        llmalert_recent_n (int): The number of most recent observations to consider.

    Returns:
        str: A prompt for the user to check if there is an anomaly in the time series data.
    """

    from tabulate import tabulate

    text_representation = tabulate(df.reset_index(), headers='keys', tablefmt='pipe', showindex=False)

    prompt = f"""
    You are a seasoned time series expert who has worked with time series data for many years and are very acomplished at spotting and explaining anomalies in time series data.

    Can you help me check if there is an anomaly in this time series data for this metric?

    I am solely interested in looking at the last {llmalert_recent_n} observations and if it looks like the more recent data may be anomalous or if it looks not all that much different from the rest of the data.

    Here are some questions to think about:

    - Is there anything unusual about the last {llmalert_recent_n} values of the metric in the df DataFrame?
    - Are there any anomalies or outliers in the recent {llmalert_recent_n} observations of metric in df?
    - Can you identify any patterns or trends in the last {llmalert_recent_n} values of the metric in df that could be indicative of an anomaly?
    - How does the distribution of the last {llmalert_recent_n} values of the metric in df compare to the distribution of the entire dataset?
    - Are there any changes in the mean, median, or standard deviation of the metric in the last {llmalert_recent_n} observations that could be indicative of an anomaly?
    - Is there a sudden increase or decrease in the metric in the last {llmalert_recent_n} observations?
    - Is there a change in the slope of the metric trend line in the last {llmalert_recent_n} observations?
    - Are there any spikes or dips in the metric in the last {llmalert_recent_n} observations?
    - Do the last {llmalert_recent_n} observations fall outside of the normal range of the metric?
    - Are there any patterns in the timing of the anomalies in the last {llmalert_recent_n} observations?

    Notes about the data:
    - The metric_value column is the raw metric value.
    - The data is ordered by the index in ascending order. So the most recent observations are at the bottom of the table.
    - Pay attention to the ordering of the data. This is time series data so the order is very important.
    - Focus only on how the most recent {llmalert_recent_n} observations and if they look anomalous or not in reference to the earlier data.
    - The data comes from a pandas dataframe.

    Here is the data (ordered in ascending order)):

    {text_representation}

    I need a yes or no answer as to if you think the recent data looks anomalous or not.

    Please also provide a description on why the metric looks anomalous if you think it does.

    Also think about and provide a confidence level on how confident ('high', 'medium', 'low') you are that the metric is anomalous.

    Please think step by step and provide a description, along with evidence, of your thought process as you go through the data.
    """

    return prompt
