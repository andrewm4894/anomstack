"""
Functions to read data from a python function.
"""

import ast

import pandas as pd
from dagster import get_dagster_logger


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


def define_fn(fn_name: str, fn: str) -> str:
    """
    Define a python function.
    """

    logger = get_dagster_logger()

    logger.info(f"fn_name: {fn_name}")
    logger.info(f"fn: {fn}")

    namespace = {}
    exec(fn, globals(), namespace)

    return namespace[fn_name]


def run_df_fn(fn_name: str, fn: str) -> pd.DataFrame:
    """
    Run a python function.
    """

    # fn_name = define_fn(fn_name, fn)
    exec(fn)

    df = locals()[fn_name]()

    return df
