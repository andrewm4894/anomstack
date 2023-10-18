"""
"""

from dagster import get_dagster_logger
import jinja2
from jinja2 import FileSystemLoader


def render(spec_key, spec, params=None) -> str:
    """
    Render from a templated spec key.
    """

    environment = jinja2.Environment(loader=FileSystemLoader('metrics/'))

    if params is None:
        params = {}

    rendered = environment.from_string(spec[spec_key])
    rendered = rendered.render(
        table_key=spec.get('table_key'),
        metric_batch=spec.get('metric_batch'),
        train_max_n=spec.get('train_max_n'),
        train_min_n=spec.get('train_min_n'),
        score_max_n=spec.get('score_max_n'),
        alert_max_n=spec.get('alert_max_n'),
        alert_threshold=spec.get('alert_threshold'),
        alert_smooth_n=spec.get('alert_smooth_n'),
        metric_name=params.get('metric_name'),
        alert_recent_n=spec.get('alert_recent_n'),
        alert_metric_timestamp_max_days_ago=spec.get('alert_metric_timestamp_max_days_ago'),
        alert_always=spec.get('alert_always'),
    )

    return rendered
