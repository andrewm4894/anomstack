from dagster import get_dagster_logger


def resample(df, freq, freq_agg):

    logger = get_dagster_logger()

    df = df.set_index('metric_timestamp')
    if freq_agg == 'mean':
        df = df.groupby('metric_name').resample(freq).mean()
    elif freq_agg == 'sum':
        df = df.groupby('metric_name').resample(freq).sum()
    else:
        raise ValueError(f"Unsupported aggregation method: {freq_agg}")
    df = df.reset_index()

    logger.debug(f"resampled data ({freq},{freq_agg}):\n{df.head()}")

    return df
