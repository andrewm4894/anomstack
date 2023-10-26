def preprocess(
    df, diff_n=0, smooth_n=0, lags_n=0, shuffle=False, dropna=True
) -> pd.DataFrame:
    """
    Prepare data for model training and scoring.

    Parameters:
        diff_n (int): The order of differencing.
        smooth_n (int): The window size for smoothing (moving average).
        lags_n (list): The list of lags to include.
    """

    X = (
        df.sort_values(by=["metric_timestamp"])
        .reset_index(drop=True)
        .set_index("metric_timestamp")
    )
    X = X[["metric_value"]]

    if diff_n > 0:
        X["metric_value"] = X["metric_value"].diff(periods=diff_n).dropna()

    if smooth_n > 0:
        X["metric_value"] = X["metric_value"].rolling(window=smooth_n).mean().dropna()

    if lags_n > 0:
        for lag in range(1, lags_n + 1):
            X[f"lag_{lag}"] = X["metric_value"].shift(lag)

    if shuffle:
        X = X.sample(frac=1)

    if dropna:
        X = X.dropna()

    return X