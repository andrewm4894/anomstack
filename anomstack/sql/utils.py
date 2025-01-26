from typing import List

import sqlglot
import sqlglot.expressions as exp


def get_columns_from_sql(sql: str) -> List[str]:
    """
    Get the columns from a SQL query.

    Args:
        sql (str): The SQL query to extract columns from.

    Returns:
        List[str]: The columns in the SQL query.
    """
    columns = []
    for expression in sqlglot.parse_one(sql).find(exp.Select).args["expressions"]:
        if isinstance(expression, exp.Alias):
            columns.append(expression.text("alias"))
        elif isinstance(expression, exp.Column):
            columns.append(expression.text("this"))
    return columns
