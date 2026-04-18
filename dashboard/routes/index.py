"""
dashboard/routes/index.py

Index

This module contains the route for the index page.

"""

from __future__ import annotations

import logging

from fasthtml.common import H2, A, Div, P, Request, Safe, Script, Title
from monsterui.all import Button, ButtonT, Card, Container, DivFullySpaced, DivLAligned, Grid, H3, Section, Subtitle, TextPresets, UkIcon
import pandas as pd

from dashboard.app import app, rt
from dashboard.batch_stats import calculate_batch_stats
from dashboard.components import create_batch_card
from dashboard.constants import DEFAULT_LAST_N
from dashboard.data import get_data
from dashboard.presentation import summarize_batches


log = logging.getLogger("anomstack_dashboard")


def get_batch_data(batch_name: str) -> pd.DataFrame:
    """Get batch data, either from cache or by fetching.

    Args:
        batch_name (str): The name of the batch to get data for.

    Returns:
        pd.DataFrame: The batch data.
    """
    if batch_name not in app.state.df_cache:
        try:
            df = get_data(
                app.state.specs_enabled[batch_name],
                last_n=DEFAULT_LAST_N,
                ensure_timestamp=True,
            )
        except Exception as e:
            log.error(f"Error getting data for batch {batch_name}: {e}")
            df = pd.DataFrame(data=[], columns=["metric_name", "metric_timestamp", "metric_value"])
        app.state.df_cache[batch_name] = df
    return app.state.df_cache[batch_name]


def get_sorted_batch_stats() -> tuple:
    """Calculate and sort batch statistics.

    Returns:
        tuple: A tuple containing the batch statistics and the sorted batch names.
    """
    # Ensure metric batches are loaded
    app.state._ensure_specs_loaded()
    app.state._ensure_metric_batches_loaded()

    batch_stats = {}
    for batch_name in app.state.metric_batches:
        df = get_batch_data(batch_name)
        batch_stats[batch_name] = calculate_batch_stats(df, batch_name)

    active_batch_names = [
        name for name, stats in batch_stats.items() if stats["latest_timestamp"] != "No data"
    ]
    empty_batch_names = [
        name for name, stats in batch_stats.items() if stats["latest_timestamp"] == "No data"
    ]

    sorted_batch_names = sorted(
        active_batch_names,
        key=lambda x: (
            -batch_stats[x]["alert_count"],
            -batch_stats[x]["avg_score"],
        ),
    )
    empty_batch_names.sort()

    return batch_stats, sorted_batch_names, empty_batch_names


def create_overview_cards(batch_stats: dict, sorted_batch_names: list) -> Grid:
    """Create the homepage overview cards."""
    summary = summarize_batches(batch_stats, sorted_batch_names)
    cards = [
        ("Active batches", summary["active_batches"], "Batches with recent metric data."),
        ("Configured batches", summary["configured_batches"], "All enabled dashboard batches."),
        ("Tracked metrics", summary["tracked_metrics"], "Unique metrics across active batches."),
        ("Alerts in view", summary["alerts"], f"Across the default {DEFAULT_LAST_N} window."),
    ]

    return Grid(
        *[
            Card(
                P(label, cls="overview-label"),
                H3(str(value), cls="overview-value"),
                P(help_text, cls=TextPresets.muted_sm),
                cls="overview-card",
            )
            for label, value, help_text in cards
        ],
        cols_min=1,
        cols_max=4,
        cols_md=2,
        cols_lg=4,
        cols_xl=4,
        cls="dashboard-overview-grid",
    )


def create_empty_batches_section(empty_batch_names: list) -> Card | None:
    """Create a secondary section for configured batches that have no data."""
    if not empty_batch_names:
        return None

    return Card(
        DivFullySpaced(
            Div(
                H3("Configured but waiting for data"),
                Subtitle(
                    "These metric batches are enabled in config but do not have recent rows in the current data source."
                ),
                cls="space-y-1",
            ),
            P(f"{len(empty_batch_names)} pending", cls="dashboard-pill"),
        ),
        Div(
            *[P(name.replace('_', ' ').replace('-', ' ').title(), cls="dashboard-pill") for name in empty_batch_names],
            cls="no-data-pills",
        ),
        cls="empty-batches-card",
    )


def create_main_content(batch_stats: dict, sorted_batch_names: list, empty_batch_names: list) -> Div:
    """Create the main dashboard content.

    Args:
        batch_stats (dict): The batch statistics.
        sorted_batch_names (list): The sorted batch names.

    Returns:
        Div: The main dashboard content.
    """
    return Div(
        Container(
            Section(
                Card(
                    DivFullySpaced(
                        Div(
                            P("Dashboard", cls="overview-label"),
                            H2("Anomstack", cls="text-3xl font-bold mt-2"),
                            Subtitle("Painless open source anomaly detection for your metrics."),
                            cls="space-y-1",
                        ),
                        DivLAligned(
                            Button(
                                DivLAligned(
                                    UkIcon("refresh-ccw"),
                                    P("Refresh data", cls="hidden sm:inline"),
                                    cls="space-x-2",
                                ),
                                cls=ButtonT.primary,
                                hx_post="/refresh-all",
                                hx_target="#main-content",
                                hx_indicator="#loading",
                                uk_tooltip="Refresh all batch summaries",
                                aria_label="Refresh all batch summaries",
                            ),
                            A(
                                DivLAligned(
                                    UkIcon("github"),
                                    P("GitHub", cls="hidden sm:inline"),
                                    cls="space-x-2",
                                ),
                                href="https://github.com/andrewm4894/anomstack",
                                cls=ButtonT.secondary,
                                uk_tooltip="View the source code on GitHub",
                                target="_blank",
                            ),
                            cls="space-x-2",
                        ),
                        cls="homepage-hero-header",
                    ),
                    create_overview_cards(batch_stats, sorted_batch_names),
                    cls="dashboard-hero-card",
                ),
                cls="pt-6 pb-4",
            ),
            (
                Section(
                    DivFullySpaced(
                        Div(
                            H3("Active metric batches"),
                            Subtitle("Sorted by anomaly activity so the noisiest sources rise to the top."),
                            cls="space-y-1",
                        ),
                        P(f"{len(sorted_batch_names)} live", cls="dashboard-pill"),
                    ),
                    Grid(
                        *[create_batch_card(name, batch_stats[name]) for name in sorted_batch_names],
                        cols_min=1,
                        cols_max=3,
                        cols_md=2,
                        cols_lg=3,
                        cols_xl=3,
                        cls="gap-5",
                    ),
                    cls="space-y-4",
                )
                if sorted_batch_names
                else Section(
                    Card(
                        DivLAligned(
                            UkIcon("alert-triangle"),
                            P(
                                "No metric batches with recent data were found. Start Dagster or point the dashboard at a populated database.",
                                cls=TextPresets.muted_sm,
                            ),
                            cls="space-x-2",
                        ),
                        cls="empty-batches-card",
                    ),
                    cls="space-y-4",
                )
            ),
            Section(create_empty_batches_section(empty_batch_names), cls="space-y-4")
            if empty_batch_names
            else None,
            cls="dashboard-shell",
        ),
        id="main-content",
    )


@rt("/refresh-all")
def post(request: Request):
    """Refresh all batch data.

    Args:
        request (Request): The request object.

    Returns:
        list: The index route.
    """
    try:
        app.state.df_cache.clear()
        app.state.stats_cache.clear()
        app.state.chart_cache.clear()
        return index(request)
    except Exception as e:
        log.error(f"Error refreshing all batch data: {e}")
        return []


@rt
def index(request: Request):
    """Index route for the dashboard.

    Args:
        request (Request): The request object.

    Returns:
        The index route.
    """
    is_htmx = request.headers.get("HX-Request") == "true"

    script = Script(
        f"""
        (() => {{
            const isDark = {'true' if app.state.dark_mode else 'false'};
            document.documentElement.classList.toggle('dark', isDark);
            document.body.classList.toggle('dark-mode', isDark);
        }})();
    """
    )

    batch_stats, sorted_batch_names, empty_batch_names = get_sorted_batch_stats()
    main_content = create_main_content(batch_stats, sorted_batch_names, empty_batch_names)

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
