from dagster import get_dagster_logger
import pandas as pd
import jinja2


def render_sql(sql_key, spec) -> str:
    environment = jinja2.Environment()
    sql = environment.from_string(spec[sql_key])
    sql = sql.render(
        table_key=spec.get('table_key'),
        metric_batch=spec.get('metric_batch')
    )
    return sql


def read_sql(sql) -> pd.DataFrame:
    logger = get_dagster_logger()
    logger.info(f'sql:\n{sql}')
    df = pd.read_gbq(query=sql)
    logger.info(f'df:\n{df}')
    return df