"""
dashboard/routes/toggles.py

Routes for handling toggle functionality.

This module contains the routes for handling toggle functionality.

"""

from fasthtml.common import Div, Request, Script

from dashboard.app import app, rt

from .batch import get_batch_view


@rt("/batch/{batch_name}/toggle-size")
def post(batch_name: str, request: Request):
    """Toggle chart size."""
    app.state.small_charts = not app.state.small_charts
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, request, initial_load=10)


@rt("/batch/{batch_name}/toggle-columns")
def post(batch_name: str, request: Request):
    """Toggle number of columns."""
    app.state.two_columns = not app.state.two_columns
    return get_batch_view(batch_name, request, initial_load=10)


@rt("/batch/{batch_name}/toggle-markers")
def post(batch_name: str, request: Request):
    """Toggle chart markers."""
    app.state.show_markers = not app.state.show_markers
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, request, initial_load=10)


@rt("/batch/{batch_name}/toggle-legend")
def post(batch_name: str, request: Request):
    """Toggle chart legend."""
    app.state.show_legend = not app.state.show_legend
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, request, initial_load=10)


@rt("/batch/{batch_name}/toggle-line-width")
def post(batch_name: str, request: Request):
    """Toggle line width."""
    app.state.narrow_lines = not getattr(app.state, "narrow_lines", False)
    app.state.line_width = 1 if app.state.narrow_lines else 2
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, request, initial_load=10)


@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str, request: Request) -> Div:
    """Toggle theme."""
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()
    mode = "dark" if app.state.dark_mode else "light"
    script = Script(
        f"""
        (() => {{
            const franken = JSON.parse(localStorage.getItem("__FRANKEN__") || "{{}}");
            franken.mode = "{mode}";
            localStorage.setItem("__FRANKEN__", JSON.stringify(franken));
            document.documentElement.classList.toggle("dark", {str(app.state.dark_mode).lower()});
            document.body.classList.toggle("dark-mode", {str(app.state.dark_mode).lower()});
        }})();
        """
    )
    response = get_batch_view(batch_name, request, initial_load=10)
    return Div(script, response)
