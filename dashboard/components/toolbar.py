"""
dashboard/components/toolbar.py

Toolbar-related components.

This module contains the components for the toolbar.

"""

from fasthtml.common import Div
from monsterui.all import Button, ButtonT, DivLAligned, UkIcon

from .batch import create_batches_dropdown
from .settings import create_settings_dropdown


def create_toolbar_buttons(batch_name: str) -> Div:
    """Create the toolbar buttons.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        Div: The toolbar buttons.
    """
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
            DivLAligned(UkIcon("settings")),
            cls=ButtonT.secondary,
            uk_tooltip="Customize chart display settings",
        ),
        create_settings_dropdown(batch_name),
        Button(
            DivLAligned(UkIcon("refresh-ccw")),
            hx_get=f"/batch/{batch_name}/refresh",
            hx_target="#main-content",
            cls=ButtonT.secondary,
            uk_tooltip="Refresh metrics data from source",
        ),
        Button(
            DivLAligned(UkIcon("alert-circle")),
            hx_get=f"/batch/{batch_name}/anomalies",
            hx_push_url=f"/batch/{batch_name}/anomalies",
            hx_target="#main-content",
            cls=ButtonT.secondary,
            uk_tooltip="View anomaly list",
        ),

        cls="flex items-center space-x-2 flex-wrap",
    )
