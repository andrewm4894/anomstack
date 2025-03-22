"""
dashboard/routes/search.py

Routes for search and load more functionality.

This module contains the routes for the search and load more functionality.

"""

from fasthtml.common import *
from monsterui.all import *

from dashboard.app import app, rt
from .batch_view import ChartManager, get_batch_view, DEFAULT_LOAD_N_CHARTS
from dashboard.data import get_data


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
                P("No matching metrics found",
                  cls="text-muted-foreground p-4 text-center"),
                id="charts-grid",
            )

        return Div(
            *[
                ChartManager.create_chart_placeholder(stat["metric_name"],
                                                      original_index,
                                                      batch_name)
                for original_index, stat in filtered_stats_with_indices
            ],
            id="charts-grid",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4")
    except re.error:
        return Div(
            P("Invalid search pattern", cls="text-red-500 p-4 text-center"),
            id="charts-grid",
        )


@rt("/batch/{batch_name}/load-more/{start_index}")
def get(batch_name: str, start_index: int):
    """Load more charts."""
    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - (start_index + 10)
    load_next = min(10, remaining_metrics)

    return [
        *[
            ChartManager.create_chart_placeholder(
                stat["metric_name"], i, batch_name) for i, stat in enumerate(
                    metric_stats[start_index:start_index + 10],
                    start=start_index,
                )
        ],
        Div(
            Button(
                (f"Load next {load_next} of {remaining_metrics}"
                 if remaining_metrics > 0 else "No more metrics"),
                hx_get=f"/batch/{batch_name}/load-more/{start_index + 10}",
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
        return get_batch_view(batch_name, initial_load=DEFAULT_LOAD_N_CHARTS)
    except ValueError as e:
        return Div(
            P(str(e), cls="text-red-500 p-4 text-center"),
            id="main-content",
        )
