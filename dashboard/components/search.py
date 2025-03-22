"""
Search and filtering components.
"""
from fasthtml.common import *
from monsterui.all import *
from dashboard.state import get_state

def create_search_form(batch_name: str) -> Form:
    """Create the search form."""
    state = get_state()
    current_search = state.search_term.get(batch_name, "")

    return Form(
        Input(
            type="search",
            name="search",
            placeholder="Search metrics...",
            value=current_search,
            cls="uk-input uk-form-small rounded-md border-gray-200 w-full md:w-[220px]",
            uk_tooltip="Filter metrics by name",
            autocomplete="off",
            aria_label="Search metrics",
        ),
        hx_get=f"/batch/{batch_name}/search",
        hx_target="#charts-container",
        hx_trigger="input changed delay:300ms, search",
        hx_indicator="#loading",
        hx_swap="outerHTML",
        onsubmit="return false;",
        cls="w-full md:w-auto",
    )

def create_last_n_form(batch_name: str) -> Form:
    """Create the last n number form."""
    state = get_state()
    return Form(
        DivLAligned(
            Input(
                type="text",
                name="last_n",
                value=state.last_n.get(batch_name, "30n"),
                pattern=r"^\d+[nNhmd]$",
                title="Use format: 30n (observations), 24h (hours), 45m (minutes), 7d (days)",
                cls="uk-input uk-form-small rounded-md border-gray-200 w-full md:w-[110px]",
                uk_tooltip="Filter by last N observations or time period (e.g., 30n, 24h, 45m, 7d)",
            ),
            cls="space-x-2",
        ),
        hx_post=f"/batch/{batch_name}/update-n",
        hx_target="#main-content",
    ) 