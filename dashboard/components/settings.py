"""
dashboard/components/settings.py

Settings-related components.

This module contains the components for the settings dropdown menu.

"""

from fasthtml.common import A, Li
from monsterui.all import DropDownNavContainer, NavDividerLi, NavHeaderLi

from dashboard.app import app


def create_settings_button(text: str, batch_name: str, action: str, tooltip: str) -> Li:
    """Create a settings dropdown button.

    Args:
        text (str): The text to display on the button.
        batch_name (str): The name of the batch.
        action (str): The action to perform when the button is clicked.
        tooltip (str): The tooltip to display when the button is hovered over.

    Returns:
        Li: The settings dropdown button.
    """
    return Li(
        A(
            text,
            hx_post=f"/batch/{batch_name}/{action}",
            hx_target="#main-content",
            uk_tooltip=tooltip,
        )
    )


def create_settings_dropdown(batch_name: str) -> DropDownNavContainer:
    """Create the settings dropdown menu.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        DropDownNavContainer: The settings dropdown menu.
    """
    buttons = [
        (
            "Use spacious charts" if app.state.small_charts else "Use compact charts",
            "toggle-size",
            "Toggle between compact and full-size chart views",
        ),
        (
            "Use two columns" if not app.state.two_columns else "Use one column",
            "toggle-columns",
            "Display charts in one or two columns",
        ),
        (
            "Hide markers" if app.state.show_markers else "Show markers",
            "toggle-markers",
            "Show/hide data point markers on the charts",
        ),
        (
            "Hide legend" if app.state.show_legend else "Show legend",
            "toggle-legend",
            "Display chart legends",
        ),
        (
            "Use normal lines" if app.state.line_width != 2 else "Use narrow lines",
            "toggle-line-width",
            "Toggle between narrow and normal line thickness",
        ),
    ]

    menu_items = [
        create_settings_button(text, batch_name, action, tooltip)
        for text, action, tooltip in buttons
    ]

    menu_items.extend(
        [
            NavDividerLi(),
            create_settings_button(
                "Use dark mode" if not app.state.dark_mode else "Use light mode",
                batch_name,
                "toggle-theme",
                "Switch between light and dark color themes",
            ),
        ]
    )

    return DropDownNavContainer(
        NavHeaderLi("settings"),
        *menu_items,
    )
