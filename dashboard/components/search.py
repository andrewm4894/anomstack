"""
dashboard/components/search.py

Search and filtering components.

This module contains the components for the search and filtering functionality.

"""

from fasthtml.common import Div, Label, P
from monsterui.all import DivLAligned, Form, Input

from dashboard.app import app


def create_search_form(batch_name: str) -> Form:
    """Create the search form.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        Form: The search form.
    """
    current_search = app.state.search_term.get(batch_name, "")

    return Form(
        Label("Search metrics", fr="metric-search", cls="text-sm font-medium"),
        Input(
            id="metric-search",
            type="search",
            name="search",
            placeholder="Name or regular expression…",
            value=current_search,
            cls="uk-input uk-form-small rounded-md border-gray-200 w-full md:w-[220px]",
            uk_tooltip="Filter metric names with a case-insensitive regular expression",
            autocomplete="off",
            aria_label="Search metrics",
            hx_get=f"/batch/{batch_name}/search",
            hx_target="#charts-container",
            hx_swap="outerHTML",
            hx_trigger="input changed delay:300ms, search",
            hx_indicator="#loading",
            hx_sync="closest form:abort",
            _="on htmx:afterRequest if event.detail.successful console.log('Search completed')",
        ),
        id=f"search-form-{batch_name}",
        onsubmit="return false;",
        cls="w-full md:w-auto",
    )


def create_last_n_form(batch_name: str) -> Form:
    """Create the last n number form.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        Form: The last n number form.
    """
    current_last_n = app.state.last_n.get(batch_name, "90n")

    return Form(
        Label("Time window", fr="time-window", cls="text-sm font-medium"),
        DivLAligned(
            Input(
                id="time-window",
                aria_describedby="time-window-help",
                type="text",
                name="last_n",
                value=current_last_n,
                pattern=r"^\d+[nNhmd]$",
                title="Use format: 90n (observations), 24h (hours), 45m (minutes), 7d (days)",
                cls="uk-input uk-form-small rounded-md border-gray-200 w-full md:w-[110px]",
                uk_tooltip="Filter by last N observations or time period (e.g., 90n, 24h, 45m, 7d)",
                hx_trigger="change delay:500ms",
                hx_post=f"/batch/{batch_name}/update-n",
                hx_target="#charts-container",
                hx_swap="outerHTML",
                hx_indicator="#loading",
                hx_sync="closest form:abort",
            ),
            cls="space-x-2",
        ),
        P(
            "90n = 90 points · 24h = 24 hours · 7d = 7 days",
            id="time-window-help",
            cls="text-xs text-muted-foreground mt-1",
        ),
        Div(id="window-error"),
        id=f"last-n-form-{batch_name}",
        onsubmit="return false;",
    )
