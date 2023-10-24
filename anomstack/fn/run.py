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


def run_fn(fn, fn_name) -> pd.DataFrame:
    """
    Run a python function.
    """

    logger = get_dagster_logger()

    logger.info(f'fn:\n{fn}')

    # validate function definition
    if not validate_function_definition(fn, fn_name):
        raise ValueError(f"'fn' does not define a function named '{fn_name}'")

    exec(fn)

    df = locals()[fn_name]()

    return df
