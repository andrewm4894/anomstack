"""
"""

import jinja2
from jinja2 import FileSystemLoader


def rendered_translated(db, rendered_str, context):
    """
    Apply database-specific replacements to the template string.
    """
    rendered_str_translated = rendered_str
    if db == "snowflake":
        alert_metric_timestamp_max_days_ago = context[
            "alert_metric_timestamp_max_days_ago"
        ]
        rendered_str_translated = rendered_str_translated.replace(
            f"CURRENT_DATE - INTERVAL '{alert_metric_timestamp_max_days_ago}' DAY",
            f"DATEADD(day, -{alert_metric_timestamp_max_days_ago}, CURRENT_TIMESTAMP)",
        )
    return rendered_str_translated


def render(spec_key, spec, params=None) -> str:
    """
    Render from a templated spec key.
    """

    environment = jinja2.Environment(loader=FileSystemLoader("metrics/"))

    params = {} if params is None else params

    db = spec["db"]
    template_str = spec[spec_key]

    template = environment.from_string(template_str)

    # Prepare context by starting with spec, then update with params
    # Any key that exists in both will have the value from params
    context = {**spec, **params}

    # Render the template with the context
    rendered = template.render(**context)

    rendered = rendered_translated(db, rendered, context)

    return rendered
