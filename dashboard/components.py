"""
Components for the dashboard.
"""

from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

from state import get_state
from constants import *


def _create_controls(batch_name):
    """
    Create the controls for the dashboard.
    """
    state = get_state()
    settings_dropdown = DropDownNavContainer(
        NavHeaderLi("Settings"),
        Li(
            DivLAligned(
                Button(
                    P("Small Charts", cls="text-sm font-medium"),
                    hx_post=f"/batch/{batch_name}/toggle-size",
                    hx_target="#main-content",
                    cls=ButtonT.ghost,
                    uk_tooltip="Toggle between compact and full-size chart views",
                ),
                cls="flex items-center justify-between w-full px-2 py-2",
            )
        ),
        Li(
            DivLAligned(
                Button(
                    P("Two Columns", cls="text-sm font-medium"),
                    hx_post=f"/batch/{batch_name}/toggle-columns",
                    hx_target="#main-content",
                    cls=ButtonT.ghost,
                    uk_tooltip="Display charts in one or two columns",
                ),
                cls="flex items-center justify-between w-full px-2 py-2",
            )
        ),
        Li(
            DivLAligned(
                Button(
                    P("Show Markers", cls="text-sm font-medium"),
                    hx_post=f"/batch/{batch_name}/toggle-markers",
                    hx_target="#main-content",
                    cls=ButtonT.ghost,
                    uk_tooltip="Show/hide data point markers on the charts",
                ),
                cls="flex items-center justify-between w-full px-2 py-2",
            )
        ),
        Li(
            DivLAligned(
                Button(
                    P("Show Legend", cls="text-sm font-medium"),
                    hx_post=f"/batch/{batch_name}/toggle-legend",
                    hx_target="#main-content",
                    cls=ButtonT.ghost,
                    uk_tooltip="Display chart legends",
                ),
                cls="flex items-center justify-between w-full px-2 py-2",
            )
        ),
        Li(
            DivLAligned(
                Button(
                    P("Narrow Lines", cls="text-sm font-medium"),
                    hx_post=f"/batch/{batch_name}/toggle-line-width",
                    hx_target="#main-content",
                    cls=ButtonT.ghost,
                    uk_tooltip="Toggle between narrow and normal line thickness",
                ),
                cls="flex items-center justify-between w-full px-2 py-2",
            )
        ),
        NavDividerLi(),
        Li(
            DivLAligned(
                Button(
                    P("Dark Mode", cls="text-sm font-medium"),
                    hx_post=f"/batch/{batch_name}/toggle-theme",
                    hx_target="#main-content",
                    cls=ButtonT.ghost,
                    uk_tooltip="Switch between light and dark color themes",
                ),
                cls="flex items-center justify-between w-full px-2 py-2",
            )
        ),
    )

    batches_dropdown = DropDownNavContainer(
        NavHeaderLi("Metric Batches"),
        *[
            Li(
                A(
                    batch_name,
                    hx_get=f"/batch/{batch_name}",
                    hx_push_url=f"/batch/{batch_name}",
                    hx_target="#main-content",
                    hx_indicator="#loading",
                    cls=f"{'uk-active' if batch_name == batch_name else ''}",
                )
            )
            for batch_name in state.metric_batches
        ],
    )

    return Card(
        DivFullySpaced(
            Div(
                Div(
                    Div(
                        Div(
                            Div(
                                Div(
                                    Button(
                                        DivLAligned(UkIcon("home")),
                                        hx_get="/",
                                        hx_push_url="/",
                                        hx_target="#main-content",
                                        cls=ButtonT.secondary,
                                        uk_tooltip="Return to homepage",
                                    ),
                                    Button(
                                        DivLAligned(UkIcon("refresh-ccw")),
                                        hx_get=f"/batch/{batch_name}/refresh",
                                        hx_target="#main-content",
                                        cls=ButtonT.secondary,
                                        uk_tooltip="Refresh metrics data from source",
                                    ),
                                    cls="flex items-center space-x-2",
                                ),
                                Div(
                                    Button(
                                        DivLAligned(UkIcon("menu")),
                                        cls=ButtonT.secondary,
                                        uk_tooltip="Select metric batch to display",
                                    ),
                                    batches_dropdown,
                                    Button(
                                        DivLAligned(UkIcon("settings")),
                                        cls=ButtonT.secondary,
                                        uk_tooltip="Customize chart display settings",
                                    ),
                                    settings_dropdown,
                                    A(
                                        DivLAligned(UkIcon("github")),
                                        href="https://github.com/andrewm4894/anomstack",
                                        target="_blank",
                                        cls="uk-button uk-button-secondary",
                                        uk_tooltip="View project on GitHub",
                                    ),
                                    cls="flex items-center space-x-2",
                                ),
                                cls="flex flex-row items-center space-x-2 flex-wrap justify-between",
                            ),
                            Div(
                                _create_search_form(batch_name),
                                _create_last_n_form(batch_name),
                                cls="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-4 mt-4",
                            ),
                            cls="flex flex-col w-full",
                        ),
                    ),
                    cls="w-full",
                ),
                cls="w-full",
            ),
        ),
        cls="mb-4 uk-padding-small py-2 shadow-sm",
    )


def _create_search_form(batch_name):
    """
    Create the search form for the dashboard.
    """
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


def _create_last_n_form(batch_name):
    """
    Create the last n number form for the dashboard.
    """
    state = get_state()
    current_value = state.last_n.get(batch_name, "30n")
    return Form(
        DivLAligned(
            Input(
                type="text",
                name="last_n",
                value=current_value,
                pattern=r"\d+[nNhmd]$",
                title="Use format: 30n (observations), 24h (hours), 45m (minutes), 7d (days)",
                cls="uk-input uk-form-small uk-form-width-small",
                uk_tooltip="Filter by last N observations or time period (e.g., 30n, 24h, 45m, 7d)",
                _="on keyup[key=='Enter'] call preventDefault() then set my value to my value then trigger post on closest <form/>",
                hx_post=f"/batch/{batch_name}/update-n",
                hx_target="#main-content",
                hx_include="this",
            ),
            cls="space-x-2",
        )
    )


def create_batch_card(batch_name: str, stats: dict) -> Card:
    """Create a card displaying batch information."""
    return Card(
        DivLAligned(
            Div(
                Button(
                    batch_name,
                    hx_get=f"/batch/{batch_name}",
                    hx_push_url=f"/batch/{batch_name}",
                    hx_target="#main-content",
                    hx_indicator="#loading",
                    cls=(ButtonT.primary, "w-full")
                ),
                DividerLine(),
                DivLAligned(
                    Div(
                        DivLAligned(
                            UkIcon("activity", cls="text-blue-500"),
                            P(
                                f"{stats['unique_metrics']} metrics",
                                cls=TextPresets.muted_sm,
                            ),
                            cls="space-x-2",
                        ),
                        DivLAligned(
                            UkIcon("clock", cls="text-green-500"),
                            P(f"{stats['latest_timestamp']}", cls=TextPresets.muted_sm),
                            cls="space-x-2",
                        ),
                        DivLAligned(
                            UkIcon("bar-chart", cls="text-purple-500"),
                            P(
                                f"Avg Score: {stats['avg_score']:.1%}",
                                cls=TextPresets.muted_sm,
                            ),
                            cls="space-x-2",
                        ),
                        DivLAligned(
                            UkIcon("alert-circle", cls="text-red-500"),
                            P(
                                f"{stats['alert_count']} alerts",
                                cls=TextPresets.muted_sm,
                            ),
                            cls="space-x-2",
                        ),
                        cls="space-y-1",
                    )
                ),
                cls="w-full",
            ),
            cls="w-full",
        ),
        cls="px-2 py-0.5 hover:border-primary transition-colors duration-200",
    )


def create_header() -> Div:
    """Create the dashboard header."""
    return DivLAligned(
        H2(
            "Anomstack",
            P(
                "Painless open source anomaly detection for your metrics 📈📉🚀",
                cls=TextPresets.muted_sm,
            ),
            cls="mb-2",
        ),
        A(
            DivLAligned(UkIcon("github")),
            href="https://github.com/andrewm4894/anomstack",
            target="_blank",
            cls="uk-button uk-button-secondary",
            uk_tooltip="View on GitHub",
        ),
        style="justify-content: space-between;",
        cls="mb-6",
    )