"""
Some helper functions for rendering templates.
"""

import jinja2
from jinja2 import FileSystemLoader


def rendered_translated(db: str, rendered_str: str, context: dict) -> str:
    """
    Apply database-specific replacements to the template string.

    Args:
        db (str): The database type.
        rendered_str (str): The template string to be rendered.
        context (dict): The context containing the variables for rendering.

    Returns:
        str: The rendered and translated template string.
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


def render(spec_key: str, spec: dict, params: dict = None) -> str:
    """
    Render from a templated spec key.

    Args:
        spec_key (str): The key of the template in the spec.
        spec (dict): The spec containing the templates.
        params (dict, optional): The parameters for rendering the template. Defaults to None.

    Returns:
        str: The rendered template string.
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
