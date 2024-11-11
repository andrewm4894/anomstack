def ingest():
    """
    Generate random metrics data with occasional anomalies (spikes, drops,
    or plateaus).
    """

    import random

    import pandas as pd

    # Define the number of metrics
    metrics = ["metric1", "metric2", "metric3", "metric4", "metric5"]
    metric_values = []

    # Different anomaly types
    anomaly_types = ["spike", "drop", "plateau"]

    # Generate random metrics and introduce occasional anomalies (1% chance)
    anomaly_chance = random.random()
    anomaly_type = (random.choice(anomaly_types)
                    if anomaly_chance <= 0.01 else None)

    for _ in metrics:
        if anomaly_type == "spike":
            # Generate a spike (e.g., a value significantly higher than normal)
            metric_value = random.uniform(15, 30)
        elif anomaly_type == "drop":
            # Generate a drop (e.g., a negative or significantly low value)
            metric_value = random.uniform(-10, -1)
        elif anomaly_type == "plateau":
            # Generate the same value for all metrics (e.g., a plateau)
            plateau_value = random.uniform(5, 6)
            metric_values = [plateau_value] * len(metrics)
            break  # Exit the loop early since all metrics have the same value
        else:
            # Generate a normal value
            metric_value = random.uniform(0, 10)

        metric_values.append(metric_value)

    # Create a DataFrame with the metric data
    data = {
        "metric_name": metrics,
        "metric_value": metric_values,
        "metric_timestamp": pd.Timestamp.now(),
    }
    df = pd.DataFrame(data)

    return df
