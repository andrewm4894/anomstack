"""
Routes for the dashboard.
"""

import logging
import pandas as pd
from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

from app import app, rt
from constants import *
from data import get_data
from components import create_controls, create_batch_card, create_header
from charts import ChartManager
from batch_stats import calculate_batch_stats

log = logging.getLogger("anomstack")

def _get_batch_data(batch_name: str) -> pd.DataFrame:
    """Get batch data, either from cache or by fetching."""
    if batch_name not in app.state.df_cache:
        try:
            df = get_data(
                app.state.specs_enabled[batch_name],
                last_n=DEFAULT_LAST_N,
                ensure_timestamp=True
            )
        except Exception as e:
            log.error(f"Error getting data for batch {batch_name}: {e}")
            df = pd.DataFrame(
                data=[], columns=["metric_name", "metric_timestamp", "metric_value"]
            )
        app.state.df_cache[batch_name] = df
    return app.state.df_cache[batch_name]

def _get_sorted_batch_stats() -> tuple:
    """Calculate and sort batch statistics."""
    batch_stats = {}
    for batch_name in app.state.metric_batches:
        df = _get_batch_data(batch_name)
        batch_stats[batch_name] = calculate_batch_stats(df, batch_name)

    # Filter and sort batches
    filtered_batches = {
        name: stats
        for name, stats in batch_stats.items()
        if stats["latest_timestamp"] != "No Data"
    }

    sorted_batch_names = sorted(
        filtered_batches.keys(),
        key=lambda x: (
            -filtered_batches[x]["alert_count"],
            -filtered_batches[x]["avg_score"],
        ),
    )

    return batch_stats, sorted_batch_names

def _create_main_content(batch_stats: dict, sorted_batch_names: list) -> Div:
    """Create the main dashboard content."""
    return Div(
        Card(
            DivLAligned(
                Div(
                    H2("Anomstack", cls="text-2xl font-bold pl-2"),
                    P(
                        "Painless open source anomaly detection for your metrics 📈📉🚀",
                        cls="text-muted-foreground pl-2",
                    ),
                    cls="flex flex-col",
                ),
                DivLAligned(
                    Button(
                        DivLAligned(UkIcon("refresh-ccw"), cls="space-x-2"),
                        cls=ButtonT.ghost,
                        hx_post="/refresh-all",
                        hx_target="#main-content",
                        hx_indicator="#loading",
                        uk_tooltip="Refresh all",
                    ),
                    A(
                        UkIcon("github"),
                        href="https://github.com/andrewm4894/anomstack",
                        cls=ButtonT.ghost,
                        uk_tooltip="View the source code on GitHub",
                        target="_blank",
                    ),
                    cls="space-x-2",
                ),
                cls="flex justify-between items-center mb-6",
            ),
            (
                Div(
                    DivLAligned(
                        UkIcon("alert-triangle"),
                        P(
                            "No metric batches found. Is Dagster running?",
                            cls=TextPresets.muted_sm,
                        ),
                        cls="space-x-2 p-2 bg-yellow-50 text-yellow-700 rounded-md",
                    ),
                    cls="mb-6",
                )
                if not app.state.metric_batches
                else Grid(
                    *[
                        create_batch_card(name, batch_stats[name])
                        for name in sorted_batch_names
                    ],
                    cols=4,
                    gap=2,
                )
            ),
            cls="p-2",
        ),
        id="main-content",
    )

# Main Routes
@rt("/refresh-all")
def post(request: Request):
    """Refresh all batch data."""
    try:
        app.state.df_cache.clear()
        app.state.stats_cache.clear()
        app.state.chart_cache.clear()
        return [index(request)]
    except Exception as e:
        log.error(f"Error refreshing all batch data: {e}")
        return []

@rt
def index(request: Request):
    """Index route for the dashboard."""
    is_htmx = request.headers.get("HX-Request") == "true"

    # Dark mode script
    script = Script(
        f"""
        if ({'true' if app.state.dark_mode else 'false'}) {{
            document.body.classList.add('dark-mode');
        }}
    """
    )

    batch_stats, sorted_batch_names = _get_sorted_batch_stats()
    main_content = _create_main_content(batch_stats, sorted_batch_names)

    if is_htmx:
        return main_content

    return (
        Title("Anomstack"),
        script,
        Div(
            Safe('<span class="htmx-indicator">Loading...</span>'),
            id="loading",
            cls="loading-indicator",
        ),
        main_content,
    )

# Batch View Routes
@rt("/batch/{batch_name}")
def get_batch_view(batch_name: str, session, initial_load: int = DEFAULT_LOAD_N_CHARTS):
    """Get the batch view."""
    if batch_name not in app.state.df_cache or batch_name not in app.state.stats_cache:
        app.state.df_cache[batch_name] = _get_batch_data(batch_name)
        app.state.calculate_metric_stats(batch_name)

    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - initial_load

    script = Script(
        f"""
        document.querySelectorAll('.top-nav li').forEach(li => {{
            li.classList.remove('uk-active');
            if (li.querySelector('a').textContent.trim() === '{batch_name}') {{
                li.classList.add('uk-active');
            }}
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    """
    )

    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)
    return Div(
        create_controls(batch_name),
        Div(
            *[
                ChartManager.create_chart_placeholder(
                    stat["metric_name"], i, batch_name
                )
                for i, stat in enumerate(metric_stats[:initial_load])
            ],
            id="charts-container",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
        ),
        Div(
            Button(
                f"Load next {load_next} of {remaining_metrics}",
                hx_get=f"/batch/{batch_name}/load-more/{initial_load}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0,
            ),
            id="load-more-container",
        ),
        script,
    )

@rt("/batch/{batch_name}/chart/{chart_index}")
def get(batch_name: str, chart_index: int):
    """Get chart for a batch and index."""
    df = app.state.df_cache[batch_name]
    metric_stats = app.state.stats_cache[batch_name]
    metric_name = metric_stats[chart_index]["metric_name"]
    anomaly_rate = metric_stats[chart_index]["anomaly_rate"]
    avg_score = metric_stats[chart_index]["avg_score"]

    if batch_name not in app.state.chart_cache:
        app.state.chart_cache[batch_name] = {}

    if chart_index not in app.state.chart_cache[batch_name]:
        df_metric = df[df["metric_name"] == metric_name]
        fig = ChartManager.create_chart(df_metric, chart_index)
        app.state.chart_cache[batch_name][chart_index] = fig

    return Card(
        Style(
            """
            .uk-card-header { padding: 1rem; }
            .uk-card-body { padding: 1rem; }
        """
        ),
        Safe(app.state.chart_cache[batch_name][chart_index]),
        header=Div(
            H4(metric_name, cls="mb-1"),
            DivLAligned(
                P(f"Anomaly Rate: {anomaly_rate:.1%}", cls="text-sm text-muted-foreground"),
                P(f"Avg Score: {avg_score:.1%}", cls="text-sm text-muted-foreground"),
                style="gap: 1rem;",
            ),
        ),
        id=f"chart-{chart_index}",
        cls="mb-1",
    )

# Toggle Routes
def _handle_toggle_route(batch_name: str, toggle_func, session=None):
    """Generic handler for toggle routes."""
    toggle_func()
    app.state.chart_cache.clear()
    return get_batch_view(batch_name, session, initial_load=DEFAULT_LOAD_N_CHARTS)

@rt("/batch/{batch_name}/toggle-size")
def post(batch_name: str, session=None):
    """Toggle chart size."""
    return _handle_toggle_route(batch_name, lambda: setattr(app.state, 'small_charts', not app.state.small_charts), session)

@rt("/batch/{batch_name}/toggle-columns")
def post(batch_name: str, session=None):
    """Toggle number of columns."""
    return _handle_toggle_route(batch_name, lambda: setattr(app.state, 'two_columns', not app.state.two_columns), session)

@rt("/batch/{batch_name}/toggle-markers")
def post(batch_name: str, session=None):
    """Toggle chart markers."""
    return _handle_toggle_route(batch_name, lambda: setattr(app.state, 'show_markers', not app.state.show_markers), session)

@rt("/batch/{batch_name}/toggle-legend")
def post(batch_name: str, session=None):
    """Toggle chart legend."""
    return _handle_toggle_route(batch_name, lambda: setattr(app.state, 'show_legend', not app.state.show_legend), session)

@rt("/batch/{batch_name}/toggle-line-width")
def post(batch_name: str, session=None):
    """Toggle line width."""
    def toggle_line_width():
        app.state.narrow_lines = not getattr(app.state, "narrow_lines", False)
        app.state.line_width = 1 if app.state.narrow_lines else 2
    return _handle_toggle_route(batch_name, toggle_line_width, session)

@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str, session=None):
    """Toggle theme."""
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()
    script = Script("document.body.classList.toggle('dark-mode');")
    response = get_batch_view(batch_name, session, initial_load=DEFAULT_LOAD_N_CHARTS)
    return Div(script, response)

# Search and Load More Routes
@rt("/batch/{batch_name}/search")
def get(batch_name: str, search: str = ""):
    """Search metrics."""
    import re
    app.state.search_term[batch_name] = search

    if batch_name not in app.state.stats_cache:
        app.state.calculate_metric_stats(batch_name)

    try:
        pattern = re.compile(search, re.IGNORECASE) if search else None
        filtered_stats_with_indices = [
            (i, stat)
            for i, stat in enumerate(app.state.stats_cache[batch_name])
            if not pattern or pattern.search(stat["metric_name"])
        ]

        if not filtered_stats_with_indices:
            return Div(
                P("No matching metrics found", cls="text-muted-foreground p-4 text-center"),
                id="charts-grid",
            )

        return Div(
            *[
                ChartManager.create_chart_placeholder(
                    stat["metric_name"],
                    original_index,
                    batch_name
                )
                for original_index, stat in filtered_stats_with_indices
            ],
            id="charts-grid",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4"
        )
    except re.error:
        return Div(
            P("Invalid search pattern", cls="text-red-500 p-4 text-center"),
            id="charts-grid",
        )

@rt("/batch/{batch_name}/load-more/{start_index}")
def get(batch_name: str, start_index: int):
    """Load more charts."""
    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - (start_index + DEFAULT_LOAD_N_CHARTS)
    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)

    return [
        *[
            ChartManager.create_chart_placeholder(stat["metric_name"], i, batch_name)
            for i, stat in enumerate(
                metric_stats[start_index : start_index + DEFAULT_LOAD_N_CHARTS],
                start=start_index,
            )
        ],
        Div(
            Button(
                (
                    f"Load next {load_next} of {remaining_metrics}"
                    if remaining_metrics > 0
                    else "No more metrics"
                ),
                hx_get=f"/batch/{batch_name}/load-more/{start_index + DEFAULT_LOAD_N_CHARTS}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0,
            ),
            id="load-more-container",
            hx_swap_oob="true",
        ),
    ]

@rt("/batch/{batch_name}/update-n")
def post(batch_name: str, last_n: str = "30n", session=None):
    """Update time window."""
    try:
        app.state.last_n[batch_name] = last_n
        app.state.clear_batch_cache(batch_name)
        app.state.df_cache[batch_name] = get_data(
            app.state.specs_enabled[batch_name],
            last_n=last_n,
            ensure_timestamp=True
        )
        app.state.calculate_metric_stats(batch_name)
        return get_batch_view(batch_name, session, initial_load=DEFAULT_LOAD_N_CHARTS)
    except ValueError as e:
        return Div(
            P(str(e), cls="text-red-500 p-4 text-center"),
            id="main-content",
        )

@rt("/batch/{batch_name}/refresh")
def get(batch_name: str, session):
    """Refresh the batch view for a given batch name."""
    try:
        app.state.clear_batch_cache(batch_name)
        response = get_batch_view(
            batch_name, session, initial_load=DEFAULT_LOAD_N_CHARTS
        )
        return [response]
    except Exception as e:
        return []

@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str, session=None):
    """Toggle the theme of the dashboard for a given batch name."""
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()  # Clear cache to regenerate charts

    # Add script to toggle dark mode class on body
    script = Script(
        """
        document.body.classList.toggle('dark-mode');
    """
    )

    response = get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )
    return Div(script, response)

@rt("/batch/{batch_name}/toggle-columns")
def post(batch_name: str, session=None):
    """Toggle the number of columns for a given batch name."""
    app.state.two_columns = not app.state.two_columns
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )

@rt("/batch/{batch_name}/toggle-markers")
def post(batch_name: str, session=None):
    """Toggle the markers for a given batch name."""
    app.state.show_markers = not app.state.show_markers
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )

@rt("/batch/{batch_name}/toggle-legend")
def post(batch_name: str, session=None):
    """Toggle the legend for a given batch name."""
    app.state.show_legend = not app.state.show_legend
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )

@rt("/batch/{batch_name}/toggle-line-width")
def post(batch_name: str, session=None):
    """Toggle between narrow (1px) and normal (2px) line width."""
    app.state.narrow_lines = not getattr(app.state, "narrow_lines", False)
    app.state.line_width = 1 if app.state.narrow_lines else 2
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )