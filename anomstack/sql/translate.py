import re

import sqlglot


def db_translate(sql: str, db: str) -> str:
    """
    Replace some functions with their db-specific equivalents.

    Args:
        sql (str): The SQL query to be translated.
        db (str): The name of the database to which the query will be sent.

    Returns:
        str: The translated SQL query.
    """
    # Transpile the SQL query to the target database dialect
    sql = sqlglot.transpile(sql, write=db, identify=True, pretty=True)[0]
    # Replace some functions with their db-specific equivalents
    if db == "sqlite":
        sql = sql.replace("GET_CURRENT_TIMESTAMP()", "DATETIME('now')")
    elif db == "bigquery":
        sql = sql.replace("GET_CURRENT_TIMESTAMP()", "CURRENT_TIMESTAMP()")
        sql = re.sub(
            r"DATE\('now', '(-?\d+) day'\)", "DATE_ADD(CURRENT_DATE(), INTERVAL \\1 DAY)", sql
        )

    return sql
