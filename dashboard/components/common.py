"""
dashboard/components/common.py

Common components shared across the dashboard.

This module contains the common components for the dashboard.

"""

from fasthtml.common import Div, P
from monsterui.all import Card, CodeSpan, DivFullySpaced, H2, Subtitle

from dashboard.app import app
from dashboard.presentation import format_batch_name, get_filtered_metric_stats
from .search import create_last_n_form, create_search_form
from .toolbar import create_toolbar_buttons


def create_controls_summary(batch_name: str, hx_swap_oob: str | None = None) -> Div:
    """Create the summary pills shown above the batch filters."""
    total_metrics = len(app.state.stats_cache.get(batch_name, []))
    visible_metrics = len(get_filtered_metric_stats(batch_name))
    current_window = app.state.last_n.get(batch_name, "90n")

    return Div(
        P(f"{visible_metrics} of {total_metrics} metrics shown", cls="dashboard-pill"),
        P(f"Window {current_window}", cls="dashboard-pill"),
        cls="controls-pills",
        id=f"controls-summary-{batch_name}",
        hx_swap_oob=hx_swap_oob,
    )


def create_controls(batch_name: str) -> Card:
    """Create the main controls for the dashboard.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        Card: The card.
    """
    return Card(
        Div(
            DivFullySpaced(
                Div(
                    CodeSpan(batch_name),
                    H2(format_batch_name(batch_name), cls="mt-3 mb-1 text-2xl"),
                    Subtitle("Browse metrics, adjust the chart window, and inspect anomalies."),
                    cls="space-y-1",
                ),
                create_toolbar_buttons(batch_name),
                cls="controls-header",
            ),
            create_controls_summary(batch_name),
            Div(
                Div(
                    P("Filter metrics", cls="controls-label"),
                    create_search_form(batch_name),
                    cls="space-y-2 min-w-0",
                ),
                Div(
                    P("Time window", cls="controls-label"),
                    create_last_n_form(batch_name),
                    cls="space-y-2",
                ),
                cls="controls-form-grid",
            ),
            cls="space-y-5",
        ),
        cls="controls-card mb-5",
    )
