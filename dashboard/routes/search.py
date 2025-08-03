"""
dashboard/routes/search.py

Routes for search and load more functionality.

This module contains the routes for the search and load more functionality.

"""

from fasthtml.common import FT, Div, P
from monsterui.all import Button, ButtonT

from dashboard.app import app, rt
from dashboard.data import get_data

from .batch import DEFAULT_LOAD_N_CHARTS, ChartManager


@rt("/batch/{batch_name}/search")
def get(batch_name: str, search: str = "") -> FT:
    """Search metrics.

    Args:
        batch_name (str): The name of the batch.
        search (str): The search term.

    Returns:
        FT: The search results container with out-of-band load more button.
    """
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
                # Add out-of-band load more container
                Div(
                    id="load-more-container",
                    hx_swap_oob="true",
                ),
                id="charts-container",
                cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
            )

        remaining_metrics = len(filtered_stats_with_indices) - DEFAULT_LOAD_N_CHARTS
        load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)

        # Create chart placeholders
        chart_placeholders = [
            ChartManager.create_chart_placeholder(stat["metric_name"], original_index, batch_name)
            for original_index, stat in filtered_stats_with_indices[:DEFAULT_LOAD_N_CHARTS]
        ]

        # Create load more button if needed
        load_more_button = Div(
            Button(
                f"Load next {load_next} of {remaining_metrics}",
                hx_get=f"/batch/{batch_name}/load-more/{DEFAULT_LOAD_N_CHARTS}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0,
            )
            if remaining_metrics > 0
            else "",
            id="load-more-container",
            hx_swap_oob="true",
        )

        return Div(
            *chart_placeholders,
            load_more_button,
            id="charts-container",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
        )

    except re.error:
        return Div(
            P("Invalid search pattern", cls="text-red-500 p-4 text-center"),
            # Add out-of-band load more container
            Div(
                id="load-more-container",
                hx_swap_oob="true",
            ),
            id="charts-container",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
        )


@rt("/batch/{batch_name}/load-more/{start_index}")
def get(batch_name: str, start_index: int):
    """Load more charts.

    Args:
        batch_name (str): The name of the batch.
        start_index (int): The index of the first chart to load.

    Returns:
        list: The list of charts.
    """
    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - (start_index + 10)
    load_next = min(10, remaining_metrics)

    return [
        *[
            ChartManager.create_chart_placeholder(stat["metric_name"], i, batch_name)
            for i, stat in enumerate(
                metric_stats[start_index : start_index + 10],
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
def post(batch_name: str, last_n: str = "90n"):
    """Update time window."""
    try:
        # Update the last_n value
        app.state.last_n[batch_name] = last_n

        # Clear all caches for this batch
        if batch_name in app.state.df_cache:
            del app.state.df_cache[batch_name]
        if batch_name in app.state.stats_cache:
            del app.state.stats_cache[batch_name]
        if batch_name in app.state.chart_cache:
            del app.state.chart_cache[batch_name]

        # Get fresh data with new time window
        app.state.df_cache[batch_name] = get_data(
            app.state.specs_enabled[batch_name], last_n=last_n, ensure_timestamp=True
        )

        # Recalculate stats with new data
        app.state.calculate_metric_stats(batch_name)

        # Return only the charts container content
        metric_stats = app.state.stats_cache[batch_name]
        remaining_metrics = len(metric_stats) - DEFAULT_LOAD_N_CHARTS
        load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)

        return [
            Div(
                *[
                    ChartManager.create_chart_placeholder(stat["metric_name"], i, batch_name)
                    for i, stat in enumerate(metric_stats[:DEFAULT_LOAD_N_CHARTS])
                ],
                id="charts-container",
                cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
            ),
            Div(
                Button(
                    f"Load next {load_next} of {remaining_metrics}",
                    hx_get=f"/batch/{batch_name}/load-more/{DEFAULT_LOAD_N_CHARTS}",
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
    except ValueError as e:
        return Div(
            P(str(e), cls="text-red-500 p-4 text-center"),
            id="charts-container",
        )
