"""
dashboard/routes/toggles.py

Routes for handling toggle functionality.

This module contains the routes for handling toggle functionality.

"""

from fasthtml.common import Div, Script

from dashboard.app import app, rt
from .batch import get_batch_view


@rt("/batch/{batch_name}/toggle-size")
def post(batch_name: str):
    """Toggle chart size."""
    app.state.small_charts = not app.state.small_charts
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, initial_load=10)


@rt("/batch/{batch_name}/toggle-columns")
def post(batch_name: str):
    """Toggle number of columns."""
    app.state.two_columns = not app.state.two_columns
    return get_batch_view(batch_name, initial_load=10)


@rt("/batch/{batch_name}/toggle-markers")
def post(batch_name: str):
    """Toggle chart markers."""
    app.state.show_markers = not app.state.show_markers
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, initial_load=10)


@rt("/batch/{batch_name}/toggle-legend")
def post(batch_name: str):
    """Toggle chart legend."""
    app.state.show_legend = not app.state.show_legend
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, initial_load=10)


@rt("/batch/{batch_name}/toggle-line-width")
def post(batch_name: str):
    """Toggle line width."""
    app.state.narrow_lines = not getattr(app.state, "narrow_lines", False)
    app.state.line_width = 1 if app.state.narrow_lines else 2
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, initial_load=10)


@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str) -> Div:
    """Toggle theme."""
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()
    script = Script("document.body.classList.toggle('dark-mode');")
    response = get_batch_view(batch_name, initial_load=10)
    return Div(script, response)
