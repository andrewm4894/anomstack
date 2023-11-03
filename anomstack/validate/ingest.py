import pandas as pd


def validate_ingest_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the dataframe returned by an ingest function.
    """

    # validate the dataframe
    assert 'metric_name' in df.columns.str.lower(), 'metric_name column missing'
    assert 'metric_value' in df.columns.str.lower(), 'metric_value column missing'
    assert 'metric_timestamp' in df.columns.str.lower(), 'metric_timestamp column missing'
    assert len(df.columns) == 3, 'too many columns'
    assert len(df) > 0, 'no data returned'

    return df
