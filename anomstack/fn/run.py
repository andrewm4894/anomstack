"""
Functions to read data from a python function.
"""

import ast
from dagster import get_dagster_logger
import pandas as pd


def validate_function_definition(code_str: str, function_name: str) -> bool:
    """
    Check if the code_str contains a function definition with the given name.
    """
    try:
        parsed_ast = ast.parse(code_str)
        for node in parsed_ast.body:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return True
        return False
    except SyntaxError:
        return False


def run_ingest_fn(ingest_fn) -> pd.DataFrame:
    """
    Read data from a python function.
    """

    logger = get_dagster_logger()

    logger.info(f'ingest_fn:\n{ingest_fn}')

    # validate function definition
    if not validate_function_definition(ingest_fn, 'ingest'):
        raise ValueError(f"'ingest_fn' does not define a function named 'ingest'")

    exec(ingest_fn)

    df = locals()['ingest']()

    # validate the dataframe
    assert 'metric_name' in df.columns, 'metric_name column missing'
    assert 'metric_value' in df.columns, 'metric_value column missing'
    assert 'metric_timestamp' in df.columns, 'metric_timestamp column missing'
    assert len(df.columns) == 3, 'too many columns'
    assert len(df) > 0, 'no data returned'

    logger.info(f'df:\n{df}')

    return df
