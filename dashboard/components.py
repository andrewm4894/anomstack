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
                _create_search_form(batch_name),
                _create_alert_n_form(batch_name),
                style="display: flex; align-items: center; gap: 0.5rem;",
            ),
            Div(
                Button(
                    DivLAligned(UkIcon("menu")),
                    cls=ButtonT.secondary,
                    uk_tooltip="Select metric batch to display",
                ),
                batches_dropdown,
                Div(
                    Button(
                        DivLAligned(UkIcon("settings")),
                        cls=ButtonT.secondary,
                        uk_tooltip="Customize chart display settings",
                    ),
                    settings_dropdown,
                ),
                A(
                    DivLAligned(UkIcon("github")),
                    href="https://github.com/andrewm4894/anomstack",
                    target="_blank",
                    cls="uk-button uk-button-secondary",
                    uk_tooltip="View project on GitHub",
                ),
                style="display: flex; align-items: center; gap: 0.5rem;",
            ),
        ),
        cls="mb-2 uk-padding-small py-1",
    )


def _create_search_form(batch_name):
    """
    Create the search form for the dashboard.
    """
    return Form(
        Input(
            type="text",
            name="search",
            placeholder="Search metrics...",
            cls="uk-input uk-form-small",
            style="width: 200px;",
            uk_tooltip="Filter metrics by name",
        ),
        hx_post=f"/batch/{batch_name}/search",
        hx_target="#charts-container",
        hx_trigger="keyup changed delay:500ms, search",
    )


def _create_alert_n_form(batch_name):
    """
    Create the alert number form for the dashboard.
    """
    state = get_state()  # Get state instance first
    return Form(
        DivLAligned(
            Input(
                type="number",
                name="alert_max_n",
                value=state.alert_max_n.get(batch_name, DEFAULT_ALERT_MAX_N),
                min=1,
                max=1000,
                step=1,
                cls="uk-input uk-form-small uk-form-width-small",
            ),
            cls="space-x-2",
        ),
        hx_post=f"/batch/{batch_name}/update-n",
        hx_target="#main-content",
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
                    cls=(ButtonT.primary, "w-full", "space-x-2"),
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
            ),
            style="justify-content: space-between;",
            cls="flex-row items-center",
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
