"""
Some helper functions for rendering templates.
"""

import jinja2
from jinja2 import FileSystemLoader


def render(spec_key: str, spec: dict, params: dict = None) -> str:
    """
    Render from a templated spec key.

    Args:
        spec_key (str): The key of the template in the spec.
        spec (dict): The spec containing the templates.
        params (dict, optional): The parameters for rendering the template.
            Defaults to None.

    Returns:
        str: The rendered template string.
    """

    environment = jinja2.Environment(loader=FileSystemLoader("metrics/"))

    params = {} if params is None else params

    spec["db"]
    template_str = spec[spec_key]

    template = environment.from_string(template_str)

    # Prepare context by starting with spec, then update with params
    # Any key that exists in both will have the value from params
    context = {**spec, **params}

    # Render the template with the context
    rendered = template.render(**context)

    return rendered
