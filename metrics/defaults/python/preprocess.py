import pandas as pd


def preprocess(
    df,
    diff_n=1,
    smooth_n=3,
    lags_n=5,
    shuffle=False,
    dropna=True,
    freq=None,
    freq_agg="mean",
) -> pd.DataFrame:
    """
    Prepare data for model training and scoring.

    Parameters:
        diff_n (int): The order of differencing.
        smooth_n (int): The window size for smoothing (moving average).
        lags_n (list): The list of lags to include.
        shuffle (bool): Whether to shuffle the data.
        dropna (bool): Whether to drop missing values.
        freq (str): The frequency string to resample the data.
        freq_agg (str): The aggregation method for resampling.
    """

    logger = get_dagster_logger()

    logger.info(f"preprocess df shape: {df.shape}")
    X = (
        df.sort_values(by=["metric_timestamp"])
        .reset_index(drop=True)
        .set_index("metric_timestamp")
    )
    logger.info(f"preprocess X shape: {X.shape}")
    X = X[["metric_value"]]
    logger.info(f"preprocess X shape: {X.shape}")
    if freq is not None:
        if freq_agg == "mean":
            X = X.resample(freq).mean()
        elif freq_agg == "sum":
            X = X.resample(freq).sum()
        # Add other aggregation methods as needed
        else:
            raise ValueError(f"Unsupported aggregation method: {freq_agg}")

    if diff_n > 0:
        X["metric_value"] = X["metric_value"].diff(periods=diff_n).dropna()
    logger.info(f"preprocess X shape: {X.shape}")

    if smooth_n > 0:
        X["metric_value"] = X["metric_value"].rolling(window=smooth_n).mean().dropna()
    logger.info(f"preprocess X shape: {X.shape}")
    if lags_n > 0:
        for lag in range(1, lags_n + 1):
            X[f"lag_{lag}"] = X["metric_value"].shift(lag)
    logger.info(f"preprocess X shape: {X.shape}")
    if shuffle:
        X = X.sample(frac=1)
    logger.info(f"preprocess X shape: {X.shape}")
    logger.info(X)
    if dropna:
        X = X.dropna()
    logger.info(f"preprocess X shape: {X.shape}")
    return X
