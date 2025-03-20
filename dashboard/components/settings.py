
"""Settings components for the dashboard."""

from fasthtml.common import *
from monsterui.all import *

def create_settings_button(text: str, batch_name: str, action: str, tooltip: str) -> Li:
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
        ("small charts", "toggle-size", "Toggle between compact and full-size chart views"),
        ("two columns", "toggle-columns", "Display charts in one or two columns"),
        ("show markers", "toggle-markers", "Show/hide data point markers on the charts"),
        ("show legend", "toggle-legend", "Display chart legends"),
        ("narrow lines", "toggle-line-width", "Toggle between narrow and normal line thickness"),
    ]

    menu_items = [
        create_settings_button(text, batch_name, action, tooltip)
        for text, action, tooltip in buttons
    ]

    menu_items.extend([
        NavDividerLi(),
        create_settings_button("dark mode", batch_name, "toggle-theme",
                           "Switch between light and dark color themes")
    ])

    return DropDownNavContainer(NavHeaderLi("settings"), *menu_items)
