
"""Toolbar components for the dashboard."""

from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

from .settings import create_settings_dropdown
from .batch import create_batches_dropdown

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
            onclick="window.open('https://github.com/andrewm4894/anomstack', '_blank')",
            uk_tooltip="View project on GitHub",
        ),
        cls="flex items-center space-x-2 flex-wrap",
    )
