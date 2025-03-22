"""
Components for the dashboard.
"""

from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

from dashboard.state import get_state
from dashboard.constants import *


def create_settings_button(text: str, batch_name: str, action: str,
                           tooltip: str) -> Li:
    """Create a settings dropdown button."""
    return Li(
        DivLAligned(
            Button(
                P(text, cls="text-sm font-medium"),
                hx_post=f"/batch/{batch_name}/{action}",
                hx_target="#main-content",
                cls=ButtonT.ghost,
                uk_tooltip=tooltip,
            ),
            cls="flex items-center justify-between w-full py-2",
        ))


def create_settings_dropdown(batch_name: str) -> DropDownNavContainer:
    """Create the settings dropdown menu."""
    buttons = [
        ("small charts", "toggle-size",
         "Toggle between compact and full-size chart views"),
        ("two columns", "toggle-columns",
         "Display charts in one or two columns"),
        ("show markers", "toggle-markers",
         "Show/hide data point markers on the charts"),
        ("show legend", "toggle-legend", "Display chart legends"),
        ("narrow lines", "toggle-line-width",
         "Toggle between narrow and normal line thickness"),
    ]

    menu_items = [
        create_settings_button(text, batch_name, action, tooltip)
        for text, action, tooltip in buttons
    ]

    # Add theme toggle after divider
    menu_items.extend([
        NavDividerLi(),
        create_settings_button("dark mode", batch_name, "toggle-theme",
                               "Switch between light and dark color themes")
    ])

    return DropDownNavContainer(NavHeaderLi("settings"), *menu_items)


def create_batches_dropdown(batch_name: str) -> DropDownNavContainer:
    """Create the metric batches dropdown menu."""
    state = get_state()
    return DropDownNavContainer(
        NavHeaderLi("metric batches"),
        *[
            Li(
                A(
                    name,
                    hx_get=f"/batch/{name}",
                    hx_push_url=f"/batch/{name}",
                    hx_target="#main-content",
                    hx_indicator="#loading",
                    cls=f"{'uk-active' if name == batch_name else ''}",
                )) for name in state.metric_batches
        ],
        uk_dropdown=
        "pos: bottom-right; boundary: window; shift: true; flip: true;")


def create_toolbar_buttons(batch_name: str) -> Div:
    """Create the toolbar buttons."""
    return Div(
        Button(
            DivLAligned(UkIcon("home")),
            hx_get="/",
            hx_push_url="/",
            hx_target="#main-content",
            cls=ButtonT.secondary,
            uk_tooltip="Return to homepage",
        ),
        Button(
            DivLAligned(UkIcon("menu")),
            cls=ButtonT.secondary,
            uk_tooltip="Select metric batch to display",
        ),
        create_batches_dropdown(batch_name),
        Button(
            DivLAligned(UkIcon("refresh-ccw")),
            hx_get=f"/batch/{batch_name}/refresh",
            hx_target="#main-content",
            cls=ButtonT.secondary,
            uk_tooltip="Refresh metrics data from source",
        ),
        Button(
            DivLAligned(UkIcon("settings")),
            cls=ButtonT.secondary,
            uk_tooltip="Customize chart display settings",
        ),
        create_settings_dropdown(batch_name),
        Button(
            DivLAligned(UkIcon("github")),
            cls=ButtonT.secondary,
            onclick=
            "window.open('https://github.com/andrewm4894/anomstack', '_blank')",
            uk_tooltip="View project on GitHub",
        ),
        cls="flex items-center space-x-2 flex-wrap",
    )


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
            cls=
            "uk-input uk-form-small rounded-md border-gray-200 w-full md:w-[220px]",
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
                title=
                "Use format: 30n (observations), 24h (hours), 45m (minutes), 7d (days)",
                cls=
                "uk-input uk-form-small rounded-md border-gray-200 w-full md:w-[110px]",
                uk_tooltip=
                "Filter by last N observations or time period (e.g., 30n, 24h, 45m, 7d)",
            ),
            cls="space-x-2",
        ),
        hx_post=f"/batch/{batch_name}/update-n",
        hx_target="#main-content",
    )


def create_controls(batch_name: str) -> Card:
    """Create the main controls for the dashboard."""
    return Card(
        DivFullySpaced(
            Div(
                Div(
                    Div(
                        create_toolbar_buttons(batch_name),
                        Div(
                            create_search_form(batch_name),
                            create_last_n_form(batch_name),
                            cls=
                            "flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-4 mt-4",
                        ),
                        cls="flex flex-col w-full",
                    ), ),
                cls="w-full",
            ), ),
        cls="mb-4 uk-padding-small py-2 shadow-sm",
    )


def create_batch_card(batch_name: str, stats: dict) -> Card:
    """Create a card displaying batch information."""
    metric_info = [
        (UkIcon("activity",
                cls="text-blue-500"), f"{stats['unique_metrics']} metrics"),
        (UkIcon("clock",
                cls="text-green-500"), f"{stats['latest_timestamp']}"),
        (UkIcon("bar-chart", cls="text-purple-500"),
         f"Avg Score: {stats['avg_score']:.1%}"),
        (UkIcon("alert-circle",
                cls="text-red-500"), f"{stats['alert_count']} alerts"),
    ]

    metric_divs = [
        DivLAligned(
            icon,
            P(text, cls=TextPresets.muted_sm),
            cls="space-x-2",
        ) for icon, text in metric_info
    ]

    return Card(
        DivLAligned(
            Div(
                Button(batch_name,
                       hx_get=f"/batch/{batch_name}",
                       hx_push_url=f"/batch/{batch_name}",
                       hx_target="#main-content",
                       hx_indicator="#loading",
                       cls=(ButtonT.primary, "w-full")),
                DividerLine(),
                DivLAligned(Div(*metric_divs, cls="space-y-1"), ),
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
