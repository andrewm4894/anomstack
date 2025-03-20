
"""
Routes for handling toggle functionality.
"""
from fasthtml.common import *
from monsterui.all import *

from app import app, rt

@rt("/batch/{batch_name}/toggle-size")
def post(batch_name: str, session=None):
    """Toggle chart size."""
    app.state.small_charts = not app.state.small_charts
    app.state.chart_cache.clear()
    from .batch_view import get_batch_view
    return get_batch_view(batch_name, session, initial_load=10)

@rt("/batch/{batch_name}/toggle-columns")
def post(batch_name: str, session=None):
    """Toggle number of columns."""
    app.state.two_columns = not app.state.two_columns
    from .batch_view import get_batch_view
    return get_batch_view(batch_name, session, initial_load=10)

@rt("/batch/{batch_name}/toggle-markers")
def post(batch_name: str, session=None):
    """Toggle chart markers."""
    app.state.show_markers = not app.state.show_markers
    app.state.chart_cache.clear()
    from .batch_view import get_batch_view
    return get_batch_view(batch_name, session, initial_load=10)

@rt("/batch/{batch_name}/toggle-legend")
def post(batch_name: str, session=None):
    """Toggle chart legend."""
    app.state.show_legend = not app.state.show_legend
    app.state.chart_cache.clear()
    from .batch_view import get_batch_view
    return get_batch_view(batch_name, session, initial_load=10)

@rt("/batch/{batch_name}/toggle-line-width")
def post(batch_name: str, session=None):
    """Toggle line width."""
    app.state.narrow_lines = not getattr(app.state, "narrow_lines", False)
    app.state.line_width = 1 if app.state.narrow_lines else 2
    app.state.chart_cache.clear()
    from .batch_view import get_batch_view
    return get_batch_view(batch_name, session, initial_load=10)

@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str, session=None):
    """Toggle theme."""
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()
    script = Script("document.body.classList.toggle('dark-mode');")
    from .batch_view import get_batch_view
    response = get_batch_view(batch_name, session, initial_load=10)
    return Div(script, response)
