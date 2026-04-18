"""
dashboard/components/toolbar.py

Toolbar-related components.

This module contains the components for the toolbar.

"""

from __future__ import annotations

from fasthtml.common import Div, P
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
            DivLAligned(
                UkIcon("home"),
                P("Home", cls="hidden xl:inline"),
                cls="space-x-2",
            ),
            hx_get="/",
            hx_push_url="/",
            hx_target="#main-content",
            hx_indicator="#loading",
            cls=(ButtonT.secondary, "toolbar-btn"),
            uk_tooltip="Return to homepage",
            aria_label="Return to homepage",
        ),
        Button(
            DivLAligned(UkIcon("menu")),
            cls=(ButtonT.secondary, "toolbar-btn"),
            uk_tooltip="Select metric batch to display",
            aria_label="Open metric batch selector",
        ),
        create_batches_dropdown(batch_name),
        Button(
            DivLAligned(UkIcon("settings")),
            cls=(ButtonT.secondary, "toolbar-btn"),
            uk_tooltip="Customize chart display settings",
            aria_label="Open chart display settings",
        ),
        create_settings_dropdown(batch_name),
        Button(
            DivLAligned(
                UkIcon("refresh-ccw"),
                P("Refresh", cls="hidden xl:inline"),
                cls="space-x-2",
            ),
            hx_get=f"/batch/{batch_name}/refresh",
            hx_target="#main-content",
            cls=(ButtonT.secondary, "toolbar-btn"),
            uk_tooltip="Refresh metrics data from source",
            aria_label="Refresh metrics data",
        ),
        Button(
            DivLAligned(
                UkIcon("alert-circle"),
                P("Anomalies", cls="hidden xl:inline"),
                cls="space-x-2",
            ),
            hx_get=f"/batch/{batch_name}/anomalies",
            hx_push_url=f"/batch/{batch_name}/anomalies",
            hx_target="#main-content",
            cls=(ButtonT.secondary, "toolbar-btn"),
            uk_tooltip="View anomaly list",
            aria_label="View anomaly list",
        ),
        cls="toolbar-stack",
    )
