"""
"""

import jinja2
from jinja2 import FileSystemLoader


def render(spec_key, spec, params=None) -> str:
    """
    Render from a templated spec key.
    """

    environment = jinja2.Environment(loader=FileSystemLoader("metrics/"))

    # Use empty dictionary if params is None
    params = {} if params is None else params

    # Initialize the template with the spec key
    template = environment.from_string(spec[spec_key])

    # Prepare context by starting with spec, then update with params
    # Any key that exists in both will have the value from params
    context = {**spec, **params}

    # Render the template with the context
    rendered = template.render(**context)

    return rendered
