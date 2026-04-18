"""
dashboard/components/search.py

Search and filtering components.

This module contains the components for the search and filtering functionality.

"""

# from fasthtml.common import Input
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
        Input(
            type="search",
            name="search",
            placeholder="Filter metrics by name",
            value=current_search,
            cls="uk-input rounded-md border-gray-200 w-full",
            uk_tooltip="Filter metrics by metric name",
            autocomplete="off",
            aria_label="Search metrics",
            hx_get=f"/batch/{batch_name}/search",
            hx_target="#charts-container",
            hx_swap="outerHTML",
            hx_trigger="input changed delay:300ms, search",
            hx_indicator="#loading",
            hx_sync="closest form:abort",
        ),
        id=f"search-form-{batch_name}",
        onsubmit="return false;",
        cls="w-full",
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
        DivLAligned(
            Input(
                type="text",
                name="last_n",
                value=current_last_n,
                pattern=r"^\d+[nNhmd]$",
                title="Use format like 90n, 24h, 45m, or 7d",
                cls="uk-input rounded-md border-gray-200 w-full md:w-[124px]",
                uk_tooltip="Window for recent observations, for example 90n, 24h, 45m, or 7d",
                aria_label="Time window",
                hx_trigger="change delay:500ms",
                hx_post=f"/batch/{batch_name}/update-n",
                hx_target="#charts-container",
                hx_swap="outerHTML",
                hx_indicator="#loading",
                hx_sync="closest form:abort",
            ),
            cls="space-x-2",
        ),
        id=f"last-n-form-{batch_name}",
        onsubmit="return false;",
    )
