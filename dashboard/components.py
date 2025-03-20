"""
Components for the dashboard.
This file is kept for backwards compatibility.
All components have been moved to the components/ directory.
"""

from .components.toolbar import create_toolbar_buttons
from .components.settings import create_settings_dropdown
from .components.batch import create_batches_dropdown, create_batch_card
from .components.forms import create_search_form, create_last_n_form
from .components.common import create_settings_button


__all__ = [
    'create_toolbar_buttons',
    'create_settings_dropdown',
    'create_batches_dropdown',
    'create_batch_card',
    'create_search_form',
    'create_last_n_form',
    'create_settings_button',
    'create_header'
]

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
                            cls="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-4 mt-4",
                        ),
                        cls="flex flex-col w-full",
                    ), ),
                cls="w-full",
            ), ),
        cls="mb-4 uk-padding-small py-2 shadow-sm",
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