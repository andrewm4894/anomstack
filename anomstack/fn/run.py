"""
Functions to read data from a python function.
"""

import ast

from dagster import get_dagster_logger
import pandas as pd


def validate_function_definition(code_str: str, function_name: str) -> bool:
    """
    Check if the code_str contains a function definition with the given name.

    Args:
        code_str (str): The code string to parse.
        function_name (str): The name of the function to search for.

    Returns:
        bool: True if the function definition is found, False otherwise.
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

    Args:
        fn_name (str): The name of the function to define.
        fn (str): The code string representing the function.

    Returns:
        str: The name of the defined function.
    """

    logger = get_dagster_logger()

    logger.debug(f"fn_name: {fn_name}")
    logger.debug(f"fn: {fn}")

    namespace = {}
    exec(fn, globals(), namespace)

    return namespace[fn_name]


def run_df_fn(fn_name: str, fn: str) -> pd.DataFrame:
    """
    Run a python function.

    Args:
        fn_name (str): The name of the function to run.
        fn (str): The code string representing the function.

    Returns:
        pd.DataFrame: The result of running the function.
    """

    # fn_name = define_fn(fn_name, fn)
    exec(fn)

    df = locals()[fn_name]()

    return df
