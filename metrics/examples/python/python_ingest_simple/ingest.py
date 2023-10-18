def ingest():

    import pandas as pd
    import random
    import time

    # generate random metrics
    metric1_value = random.uniform(0, 10)
    metric2_value = random.uniform(0, 10)

    # get current timestamp
    current_timestamp = int(time.time())

    # make df
    data = {
        'metric_name': ['metric1', 'metric2'],
        'metric_value': [metric1_value, metric2_value],
        'metric_timestamp': [current_timestamp, current_timestamp]
        }
    df = pd.DataFrame(data)

    return df
